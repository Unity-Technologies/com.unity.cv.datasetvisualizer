resource "artifactory_group" "ai-cv-tools-local" {
  name          = "ai-cv-tools-local"
  description  = "AI Computer Vision Tools team read/write group"
}

resource "artifactory_permission_target" "ads-creative-tools-rw" {
  name = "ads-creative-tools-rw"

  repo {
    repositories = [
      "ads-npm-prod-local",
    ]

    actions {
      groups {
        name        = artifactory_group.ai-cv-tools-local.name
        permissions = ["read", "write", "delete", "annotate"]
      }
    }
  }
}