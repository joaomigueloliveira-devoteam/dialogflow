output "bgp_peers" {
  description = "BGP peer resources."
  value = {
    for k, v in google_compute_router_peer.bgp_peer : k => v
  }
}

output "external_gateway" {
  description = "External VPN gateway resource."
  value = (
    var.peer_external_gateway != null
    ? google_compute_external_vpn_gateway.external_gateway[0]
    : null
  )
}

output "gateway" {
  description = "VPN gateway resource (only if auto-created)."
  value = (
    var.vpn_gateway_create
    ? google_compute_ha_vpn_gateway.ha_gateway[0]
    : null
  )
}

output "name" {
  description = "VPN gateway name (only if auto-created). ."
  value = (
    var.vpn_gateway_create
    ? google_compute_ha_vpn_gateway.ha_gateway[0].name
    : null
  )
}

output "random_secret" {
  description = "Generated secret."
  value       = local.secret
}

output "router" {
  description = "Router resource (only if auto-created)."
  value = (
    var.router_name == ""
    ? google_compute_router.router[0]
    : null
  )
}

output "router_name" {
  description = "Router name."
  value       = local.router
}

output "self_link" {
  description = "HA VPN gateway self link."
  value       = local.vpn_gateway
}

output "tunnel_names" {
  description = "VPN tunnel names."
  value = {
    for name in keys(var.tunnels) :
    name => try(google_compute_vpn_tunnel.tunnels[name].name, null)
  }
}

output "tunnel_self_links" {
  description = "VPN tunnel self links."
  value = {
    for name in keys(var.tunnels) :
    name => try(google_compute_vpn_tunnel.tunnels[name].self_link, null)
  }
}

output "tunnels" {
  description = "VPN tunnel resources."
  value = {
    for name in keys(var.tunnels) :
    name => try(google_compute_vpn_tunnel.tunnels[name], null)
  }
}
