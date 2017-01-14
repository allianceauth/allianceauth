# Cloudflare

CloudFlare offers free SSL and DDOS mitigation services. Why not take advantage of it?

## Setup

You’ll need to register an account on [CloudFlare’s site.](https://www.cloudflare.com/)

Along the top bar, select `Add Site`

Enter your domain name. It will scan records and let you know you can add the site. Continue setup.

On the next page you should see an A record for yourdomain.com pointing at your server IP. If not, manually add one:

    A    yourdomain.com     my.server.ip.address     Automatic TTL

Add the record and ensure the cloud under Status is orange. If not, click it. This ensures traffic gets screened by CloudFlare.

If you want forums or kb on a subdomain, and want these to be protected by CloudFlare, add an additional record for for each subdomain in the following format, ensuring the cloud is orange:

    CNAME     subdomain         yourdomain.com       Automatic TTL

CloudFlare blocks ports outside 80 and 443 on hosts it protects. This means, if the cloud is orange, only web traffic will get through. We need to reconfigure AllianceAuth to provide services under a subdomain. Configure these subdomains as above, but ensure the cloud is not orange (arrow should go around a grey cloud).

## Redirect to HTTPS

Now we need to configure the https redirect to force all traffic to https. Along the top bar of CloudFlare, select `Page Rules`. Add a new rule, Pattern is yourdomain.com, toggle the `Always use https` to ON, and save. It’ll take a few minutes to propagate. 

![infographic](http://i.stack.imgur.com/VUBvo.jpg)

## Update Auth URLs

Edit settings.py and replace everything that has a HTTP with HTTPS (except anything with a port on the end, like `OPENFIRE_ADDRESS`)

And there we have it. You’re DDOS-protected with free SSL.