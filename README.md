# zkill_bot integration for Discord

## Purpose
A simple Discord integration to pull kills and losses from zkill's websocket.

## Features
- Track kills across any entity zkill emits on.
- Emit embedded Discord messages through a bot once zkill updates the kill.

## Configuration

Configuration is handled in `config.py` via a .env file:

- `TARGET_ENTITY`: The name of the entity (see entity type list).
- `TARGET_ENTITY_ID`: The ID for the entity you're tracking. Example: `https://zkillboard.com/corporation/{id}/`.
- `TARGET_DISCORD_CHANNEL_ID`: The ID of the channel you wish to emit messages to.
- `TOKEN`: The token for your bot. See the Discord developer portal to set up a bot and retrieve the key.
- `DELAY`: 1 is required. Swagger API enforces limits on how often you can request. This delay is the shortest amount of time possible without generating errors.

In the root directory, create a file and name it `.env` and open it in your favorite text editor.\
Add these 4 variables to the file and fill them out using the above and below information.\

.env
```
TARGET_ENTITY_ID=123456
TARGET_DISCORD_CHANNEL_ID=123456
TARGET_ENTITY="corporation"
TOKEN="yOUrDiSCoRd+TokEN="
```

### Entity Type List
A list of all entity types provided by zkill:

- `character`
- `corporation`
- `alliance`
- `faction`
- `ship`
- `group`
- `system`
- `constellation`
- `region`
- `location`
- `label`

The app does not support the `killstream` entity, as it only supports the simplified format.

## Run
After configuring the application, from the parent directory of the root folder run:

```bash
python3 -m astralAideKillbot.main
```
If the project is stored in `home/user/projects/astralAideKillbot`, execute the command from `home/user/projects`.
