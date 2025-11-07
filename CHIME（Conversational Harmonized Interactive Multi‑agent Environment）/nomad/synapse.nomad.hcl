# 示意模板：Matrix Synapse（简化）
job "synapse" {
  datacenters = ["dc1"]
  type = "service"
  group "synapse" {
    network { port "http" { to = 8008 } }
    task "server" {
      driver = "docker"
      config { image = "matrixdotorg/synapse:latest" ports = ["http"] }
      template { data = """# 绑定实际 homeserver.yaml 或用卷挂载
""" destination = "local/homeserver.yaml" }
      service {
        name = "synapse"
        port = "http"
        check { type = "http" path = "/_matrix/client/versions" interval = "10s" timeout = "2s" }
      }
      resources { cpu = 300 memory = 512 }
    }
  }
}
