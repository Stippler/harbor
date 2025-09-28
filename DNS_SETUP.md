# DNS Setup for deepharbor.xyz

## Domain Configuration

You need to configure your DNS records for `deepharbor.xyz` to point to your VPS IP `2.56.96.36`.

### Required DNS Records

Add these records in your domain registrar's DNS management panel:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 2.56.96.36 | 3600 |
| A | www | 2.56.96.36 | 3600 |
| CNAME | * | deepharbor.xyz | 3600 |

### Explanation

- **A record (@)**: Points the root domain `deepharbor.xyz` to your VPS IP
- **A record (www)**: Points `www.deepharbor.xyz` to your VPS IP  
- **CNAME (*)**: Wildcard record for any subdomain (optional but useful)

### DNS Propagation

- DNS changes can take up to 24-48 hours to propagate globally
- You can check propagation status using tools like:
  - https://dnschecker.org/
  - `dig deepharbor.xyz` (from command line)
  - `nslookup deepharbor.xyz`

### Testing DNS

Once DNS is propagated, test with:

```bash
# Test domain resolution
ping deepharbor.xyz
nslookup deepharbor.xyz

# Test HTTP access (after Harbor is running)
curl -I http://deepharbor.xyz:8080
curl -I https://deepharbor.xyz  # After SSL setup
```

### Common DNS Providers

**Namecheap:**
1. Login to Namecheap account
2. Go to Domain List → Manage
3. Advanced DNS tab
4. Add the A records above

**Cloudflare:**
1. Add domain to Cloudflare
2. Update nameservers at registrar
3. Add DNS records in Cloudflare dashboard
4. Set SSL mode to "Full" or "Flexible"

**GoDaddy:**
1. Login to GoDaddy
2. My Products → DNS
3. Add A records pointing to 2.56.96.36

**Google Domains:**
1. Go to DNS settings
2. Custom resource records
3. Add A records

### Troubleshooting

**Domain not resolving:**
- Check DNS records are correct
- Wait for propagation (up to 48 hours)
- Try different DNS servers (8.8.8.8, 1.1.1.1)

**SSL certificate issues:**
- Ensure domain resolves before running certbot
- Check firewall allows port 80/443
- Verify nginx configuration

**Still using IP address:**
- Harbor will fallback to IP if domain fails
- Check boat client logs for connection attempts
- Verify both URLs in config.json are correct

### After DNS Setup

Once DNS is working:

1. **Update config.json** (already done):
   - Primary: `ws://deepharbor.xyz:8080` 
   - Fallback: `ws://2.56.96.36:8080`

2. **Run VPS setup**:
   ```bash
   sudo /home/cstippel/harbor/setup_vps.sh
   ```

3. **Test connections**:
   - Web: https://deepharbor.xyz
   - Boat client will try domain first, fallback to IP

4. **Monitor logs**:
   ```bash
   sudo journalctl -u harbor -f
   ```

The system is designed to be resilient - if the domain doesn't work, everything will still function using the IP address!
