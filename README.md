# Graphical Fuzzy AHP

## Survey Platform with Multi-Modal Response Support

This software platform enables the creation and management of surveys, supporting **multiple response modalities**. Respondents can choose between:

- A **traditional textual format**, and  
- A **novel graphical interaction**,  

providing flexibility that enhances user experience and accommodates diverse research needs.

### Key Features

- **Multi-modal survey design** – Support for textual and graphical response formats  
- **Easy deployment** – Runs locally or on public web servers with minimal setup  
- **Data export** – Built-in tools to export collected responses  
- **Analytical tools** – Automatically computes:
  - **Preference vectors**
  - **Consistency ratios**  
   
These metrics are essential for **pairwise comparison-based decision-making frameworks** (e.g., AHP).

## Configuration

The application requires Docker to be installed.
If Docker is not already installed on your system, you can install it by running the following commands (in case of Debian/Ubuntu based systems):

    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt-cache policy docker-ce
    sudo apt install docker-ce
    ```

After cloning newest version of repository open file from repository `/AHP-main/frontend/src/axiosConfig.js` and set `axios.defaults.baseURL` to public address of FastAPI server, protocol (http or https) and port (default port is 8000).

Then from folder `/AHP-main` run command:

    ```bash
    docker compose up --build
    ```
## Admin access

Initial administrator username is **admin** and password **secret**.
To alter password use RethinkDB Data Explorer (exposed on 8080 port of server) and bcrypt to create password hash (could be https://bcrypt-generator.com/). Then run query:

    ```js
    r.db('test').table('users').filter({username: 'admin'}).update({password: 'bcrypted_password'})
    ```

## Add user

To add new user to platform provide its name and bcrypted password query:

    ```js
    r.db('test').table('users').insert({username: 'new_username', password: 'bcrypted_password'})
    ```

## Optional HTTPS Support

In production, HTTPS is typically handled **at the reverse proxy level**, not by Vue or FastAPI directly.
For Debian based systems you could use for delegated domain use Nginx with Certbot.

1. **Install Certbot (Let's Encrypt)**:

   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Set up Nginx config**:

   Example config:
   ```nginx
   server {
       listen 8000;
       server_name yourdomain.com;
       location / {
           proxy_pass http://localhost:8000;
           include proxy_params;
       }
   }

   server {
       listen 8080;
       server_name yourdomain.com;
       location / {
           proxy_pass http://localhost:8080;
           include proxy_params;
       }
   }

   server {
       listen 443 ssl;
       server_name yourdomain.com;

       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

       location / {
           proxy_pass http://localhost;
           include proxy_params;
       }
   }
   ```

3. **Run Certbot**:
   ```bash
   sudo certbot --nginx
   ```

---

[![DOI](https://zenodo.org/badge/971938080.svg)](https://doi.org/10.5281/zenodo.15274783)
