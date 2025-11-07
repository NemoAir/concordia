# Nomad 作业模板说明

本目录包含示意性 HCL 模板：
- `orchestrator.nomad.hcl`：Concordia Orchestrator（FastAPI）；
- `gateway-java.nomad.hcl`：Java 网关；
- `agent-llm.nomad.hcl`：玩家侧 LLM 服务代理（连接本机 Ollama）；
- `synapse.nomad.hcl` / `element.nomad.hcl`：Matrix 服务端与客户端（可选）。

注意：需要将 `<registry>`、镜像 tag、端口、证书等替换为实际值；生产环境请结合 Consul Connect/mTLS、Ingress、卷挂载与密钥管理。
