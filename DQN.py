import numpy as np
import chainer.functions as F
import chainer.links as L
import chainer
import chainerrl
import gym
import myenv
import time

# Q値を近似するニューラルネットを定義
class QFunction(chainer.Chain):
  def __init__(self, obs_size, n_actions, n_hidden_channels=2):
    super(QFunction, self).__init__()
    with self.init_scope():
      self.l1 = L.Linear(obs_size, n_hidden_channels)
      self.l2 = L.Linear(n_hidden_channels, n_hidden_channels)
      self.l3 = L.Linear(n_hidden_channels, n_hidden_channels)
      self.l4 = L.Linear(n_hidden_channels, n_actions)

  def __call__(self, x, test=False):
    x = x.astype(np.float32)
    h1 = F.relu(self.l1(x))
    h2 = F.relu(self.l2(h1))
    h3 = F.relu(self.l3(h2))
    return chainerrl.action_value.DiscreteActionValue(self.l4(h3))


def main():
  env = gym.make("Rappy-v0")
  obs_size = env.observation_space.shape[0] # プレイヤーと壁の中心との相対ベクトル(x, y)
  n_actions = env.action_space.n # jumpするかしないか
  n_nodes = 256 # 中間層のノード数
  q_func = QFunction(obs_size, n_actions, n_nodes) # Q関数のインスタンスを生成

  # パラメータの更新アルゴリズムの設定
  optimizer = chainer.optimizers.Adam(eps=1e-2) # 引数についてはAdamを勉強したほうがよさそう
  optimizer.setup(q_func)
  # 割引率
  gamma = 0.99
  # e-greedy法
  explorer = chainerrl.explorers.LinearDecayEpsilonGreedy(start_epsilon=1.0, end_epsilon=0.1, decay_steps=50000, random_action_func=env.action_space.sample)

  # 行動を保存
  replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity=10 ** 6)

  phi = lambda x: x.astype(np.float32, copy=False)

  # DQNはreplayを使用して学習する
  # replay_start_size 再生バッファのサイズがこれより小さい場合更新をスキップする。この値になるごとに更新を行う
  # update_interval 更新を行う頻度?
  # target_update_interval 更新をネットワークと同期する頻度?
  agent = chainerrl.agents.DQN(q_func, optimizer, replay_buffer, gamma, explorer, replay_start_size=1000, minibatch_size=32, update_interval=1, target_update_interval=1000, phi=phi)

  n_episodes = 20000 # 学習ゲーム回数

  for i in range(1, n_episodes + 1):
    reward = 0
    obs = env._reset() # 初期化時の状態を返す
    done = False

    R = 0 # 1エピソードの報酬の合計
    t = 0 # 経過ステップ数(フレーム数)

    render_flag = False
    if i % 100 == 0: # 何エピソードかごとに描画させる
      render_flag = True

    while not done: #and t < max_episode_len: # ゲームが終わるまで
      if render_flag:
        env._render()
      start = time.time()
      action = agent.act_and_train(obs, reward) # 状態と報酬をもとに行動を学習、決定
      elapsed_time = time.time() - start
      print ("elapsed_time:{0}".format(elapsed_time) + "[sec]" + "\n")
      obs, reward, done, _ = env._step(action) # 行動の結果を取得
      R += reward
      t += 1

    agent.stop_episode_and_train(obs, reward, done)
    print(str(t) + "\n")


if __name__ == "__main__":
  main()