from gym.envs.registration import register

register(
    id="Rappy-v0",
    entry_point="myenv.env:RappyEnv",
)