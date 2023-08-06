"""App env configuration."""
import os
import pathlib


class EnvFile(object):
    """EnvFile module."""

    file_name = ".env"

    keys = [
        "FPP_API_KEY", "FPP_API_SECRET", "SHOP",
        "SCOPES", "HOST"
    ]

    def __init__(
        self,
        client_id="", client_secret="", shop="", scopes=[], host="",
        extra={}
    ):
        """Init."""
        self.FPP_API_KEY = client_id
        self.FPP_API_SECRET = client_secret
        self.SHOP = shop
        self.SCOPES = ','.join(scopes)
        self.HOST = host
        self.EXTRA = extra

    def update(self, field, value):
        """Update env file."""
        setattr(self, field, value)
        self.write()

    def write(self):
        """Write client info to .env file."""
        lines = [
            "=".join([key, getattr(self, key, "")])
            for key in EnvFile.keys
        ]
        output = "\n".join(lines) + "\n"
        for k, v in self.EXTRA.items():
            output += f"{k}={v}\n"
        with open(EnvFile.file_name, "w") as fd:
            fd.write(output)
        print(".env saved to project root")

    @classmethod
    def read(cls, directory, overrides={}):
        """Read env file."""
        env_details = cls.parse_external_env(directory, overrides)
        return EnvFile(
            client_id=env_details.get("FPP_API_KEY", ""),
            client_secret=env_details.get("FPP_API_SECRET", ""),
            shop=env_details.get("SHOP", ""),
            scopes=env_details.get("SCOPES", []),
            host=env_details.get("HOST", ""),
            extra=env_details.get("EXTRA", {})
        )

    @classmethod
    def parse_external_env(cls, directory, overrides):
        """Parse env details."""
        env_dict = cls.parse(directory)
        env_details = {}
        extra = {}
        for k, v in env_dict.items():
            if k in EnvFile.keys:
                env_details[k] = v
            else:
                extra[k] = v
        if extra:
            env_details["EXTRA"] = extra
        if "SCOPES" in env_details:
            env_details["SCOPES"] = env_details["SCOPES"].split(",")
        return env_details

    @classmethod
    def parse(cls, directory):
        """Parse env file."""
        env_path = cls.path(directory)
        env_dict = dict()
        with pathlib.Path(env_path).open() as fd:
            for line in fd.readlines():
                line = line.strip()
                if not line:
                    continue
                k, v = line.split("=")
                k = k.strip()
                v = v.strip()
                if not k:
                    continue
                env_dict[k] = v
        return env_dict

    @classmethod
    def path(cls, directory):
        """Get env file path."""
        return os.path.join(directory, EnvFile.file_name)
