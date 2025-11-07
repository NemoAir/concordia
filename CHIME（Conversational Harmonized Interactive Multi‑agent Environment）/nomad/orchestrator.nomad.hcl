# 示意模板：Concordia Orchestrator
job "orchestrator" {
  datacenters = ["dc1"]
  type = "service"
  group "orch" {
    network { port "http" { to = 8080 } }
    task "app" {
      driver = "docker"
      config {
        image = "<registry>/concordia-orchestrator:latest"
        ports = ["http"]
      }
      env { LOG_LEVEL = "info" }
      service {
        name = "orchestrator"
        port = "http"
        check { type = "http" path = "/health" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 500 memory = 1024 }
    }
  }
}
