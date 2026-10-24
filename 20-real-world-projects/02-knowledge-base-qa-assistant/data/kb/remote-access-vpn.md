# Remote access and VPN standard

Owner: IT Infrastructure, Acme Logistics. Version 2.0, reviewed 12 March 2026. Synthetic standard for training use.

## Who can use the VPN

All employees with a company-managed laptop can use the VPN. Contractors receive VPN access only for the duration of their contract and only to the network segments listed in their access request.

## Requesting access

Request VPN access through the IT service portal using the form "Remote access request". Your line manager approves the request, then IT Infrastructure provisions it within two business days. Access to production network segments also needs approval from the system owner.

## Multi-factor authentication

The VPN requires multi-factor authentication on every connection. Allowed methods are the company authenticator app with number matching and FIDO2 hardware security keys. SMS codes are not allowed because they can be intercepted through SIM swapping.

## Session rules

VPN sessions disconnect after 12 hours or after 30 minutes without activity. Split tunnelling is disabled, so all traffic goes through the company network while you are connected. Never share your VPN session or credentials with anyone, including IT staff.
