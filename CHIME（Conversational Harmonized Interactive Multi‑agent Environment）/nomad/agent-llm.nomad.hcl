# 示意模板：玩家侧 LLM 代理（连接本机 Ollama）
job "agent-llm-<id>" {
  datacenters = ["edge"]
  type = "service"
  group "llm" {
    network { mode = "host" }
    task "llm-proxy" {
      driver = "docker"
      config { image = "<registry>/llm-proxy:latest" }
      env {
        OLLAMA_HOST = "127.0.0.1:11434"
        MODEL_NAME  = "llama3.1:8b"
      }
      service {
        name = "agent-<id>-llm"
        port = "8081"
        tags = ["model=llama3.1-8b","quant=q6"]
        check { type = "http" path = "/health" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 2000 memory = 4096 }
    }
  }
}
