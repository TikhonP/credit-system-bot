<div align="center">
    <br>
    <h1>💼 Credit System Bot</h1>
</div>

_Python/Django-ORM_ simple telegram bot for accounting finance

## 🛠️ Deployment

1. Create `.env` file in root directory and fill it with your data (see [`.env_example`](.env_example))

2. Run docker container:

    ```shell
    docker build -t credit-bot .
    docker run -d --rm --restart unless-stopped credit-bot
    ```

## 📝 License

Copyright © 2022 Tikhon Petrishchev. All rights reserved.
