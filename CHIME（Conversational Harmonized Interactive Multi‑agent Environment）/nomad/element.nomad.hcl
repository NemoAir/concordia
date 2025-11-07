# 示意模板：Element Web（静态站）
job "element" {
  datacenters = ["dc1"]
  type = "service"
  group "element" {
    network { port "http" { to = 80 } }
    task "web" {
      driver = "docker"
      config { image = "vectorim/element-web:latest" ports = ["http"] }
      template { data = """{
  "default_server_config": {"m.homeserver": {"base_url": "https://matrix.example.com", "server_name": "example.com"}}
}
""" destination = "local/config.json" }
      service {
        name = "element"
        port = "http"
        check { type = "http" path = "/" interval = "30s" timeout = "3s" }
      }
      resources { cpu = 200 memory = 256 }
    }
  }
}
