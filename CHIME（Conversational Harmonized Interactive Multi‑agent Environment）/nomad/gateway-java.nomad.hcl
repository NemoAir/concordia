# 示意模板：Java Gateway（WebFlux/WS）
job "gateway" {
  datacenters = ["dc1"]
  type = "service"
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
