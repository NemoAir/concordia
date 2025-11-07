# 部署与运维（Nomad/Consul/Ingress）

## 前置条件
- Nomad 集群已就绪，Consul 可用；
- 容器镜像仓库可访问（orchestrator、gateway、synapse、element、llm-proxy）；
- 域名与证书（网关、Synapse/Element）。

## 组件与端口
- Orchestrator：HTTP 8080（内网）；
- Gateway：HTTP/WS 8080（对外）；
- Synapse：8008（反代到 443）；Element：静态站点；
- Agent-LLM：11434（Ollama）+ 8081（llm-proxy）。

## Nomad 作业模板（示意）

### orchestrator.nomad.hcl
```hcl
job "orchestrator" {
  datacenters = ["dc1"]
  group "orch" {
    network { port "http" { to = 8080 } }
    task "app" {
      driver = "docker"
      config {
        image = "<registry>/concordia-orchestrator:latest"
        ports = ["http"]
      }
      env {
        LOG_LEVEL = "info"
      }
      service {
        name = "orchestrator"
        port = "http"
        check { type = "http" path = "/health" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 500 memory = 1024 }
    }
  }
}
```

### gateway-java.nomad.hcl
```hcl
job "gateway" {
  datacenters = ["dc1"]
  group "gw" {
    network { port "http" { to = 8080 } }
    task "app" {
      driver = "docker"
      config { image = "<registry>/gateway-java:latest" ports = ["http"] }
      env { SPRING_PROFILES_ACTIVE = "prod" }
      service {
        name = "gateway"
        port = "http"
        check { type = "http" path = "/actuator/health" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 500 memory = 1024 }
    }
  }
}
```

### agent-llm.nomad.hcl（玩家侧）
```hcl
job "agent-llm-<id>" {
  type = "service"
  datacenters = ["edge"]
  group "llm" {
    network { mode = "host" }
    task "llm-proxy" {
      driver = "docker"
      config { image = "<registry>/llm-proxy:latest" }
      env { OLLAMA_HOST = "127.0.0.1:11434" MODEL_NAME = "llama3.1:8b" }
      service {
        name = "agent-<id>-llm"
        tags = ["model=llama3.1-8b", "quant=q6"]
        port = "8081"
        check { type = "http" path = "/health" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 2000 memory = 4096 }
    }
  }
}
```

### synapse.nomad.hcl / element.nomad.hcl
- 按官方镜像与文档部署；Element 为静态站，指向 Synapse；反代与 TLS 在 Ingress 处理。

## Consul 与服务发现
- Orchestrator/Gateway 注册为服务；
- Agent-LLM 注册为 `agent-<id>-llm`；网关查询以获取 `llm_host`；
- 可选 Consul Connect sidecar 提供 mTLS；使用 Intentions 限制访问路径。

## Ingress
- Traefik/Consul API Gateway：暴露 `gateway` 与 `matrix/element`；TLS 终止；路由规则。

## 配置与密钥
- 通过 Nomad Variables/Consul KV 注入敏感变量（JWT 秘钥、数据库连接、API Key）。

## 运维建议
- 灰度发布：滚动升级，健康检查；
- 回滚机制：镜像 tag 管理；
- 容量规划：按房间并发与 LLM 时延设定 CPU/内存与副本数。

