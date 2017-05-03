# NGINX

## Overivew

Nginx (engine x) is a HTTP server known for its high performance, stability, simple configuration, and low resource consumption. Unlike traditional servers (i.e. Apache), Nginx doesn't rely on threads to serve requests, rather using an asynchronous event driven approach which permits predictable resource usage and performance under load.

If you're trying to cram Alliance Auth into a very small VPS of say, 1-2GB or less, then Nginx will be considerably friendlier to your resources compared to Apache.

You can read more about NGINX on the [NGINX wiki](https://www.nginx.com/resources/wiki/).

## Coming from Apache

If you're converting from Apache, here are some things to consider.

Nginx is lightweight for a reason. It doesn't try to do everything internally and instead concentrates on just being a good HTTP server. This means that, unlike Apache, it wont automatically run PHP scripts via mod_php and doesn't have an internal WSGI server like mod_wsgi. That doesn't mean that it can't, just that it relies on external processes to run these instead. This might be good or bad depending on your outlook. It's good because it allows you to segment your applications, restarting Alliance Auth wont impact your PHP applications. On the other hand it means more config and more management of services. For some people it will be worth it, for others losing the centralised nature of Apache may not be worth it.

```eval_rst
+-----------+----------------------------------------+
| Apache    | Nginx Replacement                      | 
+===========+========================================+
| mod_php   | php5-fpm or php7-fpm (PHP FastCGI)     | 
+-----------+----------------------------------------+
| mod_wsgi  | Gunicorn or other external WSGI server |
+-----------+----------------------------------------+

```

Your .htaccess files wont work. Nginx has a separate way of managing access to folders via the server config. Everything you can do with htaccess files you can do with Nginx config. [Read more on the Nginx wiki](https://www.nginx.com/resources/wiki/start/topics/examples/likeapache-htaccess/)

## Setting up Nginx

Install Nginx via your preferred package manager or other method. If you need help just search, there are plenty of guides on installing Nginx out there.

You will need to have [Gunicorn](gunicorn.md) or some other WSGI server setup for hosting Alliance Auth.

Create a config file in `/etc/nginx/sites-available` call it `alliance-auth.conf` or whatever your preferred name is and copy the basic config in. Make whatever changes you feel are necessary.

Create a symbolic link to enable the site `sudo ln -s /etc/nginx/sites-available/alliance-auth.conf /etc/nginx/sites-enabled/` and then reload Nginx for the config to take effect, `sudo service nginx reload` for Ubuntu.

### Basic config

```
server {
    listen 80;
    server_name example.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/allianceserver/allianceauth/static/;
        autoindex off;
    }

    # Gunicorn config goes below
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

#### Adding TLS/SSL

With [Let's Encrypt](https://letsencrypt.org/) offering free SSL certificates, there's no good reason to not run HTTPS anymore.

Your config will need a few additions once you've got your certificate.

```
    listen 443 ssl http2; # Replace listen 80; with this

    ssl_certificate           /path/to/your/cert.crt;
    ssl_certificate_key       /path/to/your/cert.key;

    ssl on;
    ssl_session_cache  builtin:1000  shared:SSL:10m;
    ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers EECDH+ECDSA+AESGCM:EECDH+aRSA+AESGCM:EECDH+ECDSA+SHA384:EECDH+ECDSA+SHA256:EECDH+aRSA+SHA384:EECDH+aRSA+SHA256:EECDH+aRSA+RC4:EECDH:EDH+aRSA:RC4:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS;
    ssl_prefer_server_ciphers on;
```

If you want to redirect all your non-SSL visitors to your secure site, below your main configs `server` block, add the following:

```
server {
    listen 80;
    server_name example.com;

    # Redirect all HTTP requests to HTTPS with a 301 Moved Permanently response.
    return 301 https://$host$request_uri;
}
```

If you have trouble with the `ssl_ciphers` listed here or some other part of the SSL config, try getting the values from [Mozilla's SSL Config Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/).
