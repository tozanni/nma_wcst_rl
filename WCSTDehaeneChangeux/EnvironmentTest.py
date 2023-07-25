"""
Environment code, should return a timestep with an observation
    timestep = env.step(action)
    agent.observe(action, next_timestep=timestep)
    agent.update()
"""

#WCST parameters (General)

import WCST
import numpy as np

#class WCST(dm_env.Environment):
class WCST_Env():
    ACTIONS = [0, 1, 2, 3]
    
    def __init__(self,
               #N=2,
               episode_steps=32,
               #stimuli_choices=list('ABCDEF'),
               seed=1,
               ):
        """
        Args:
        episode_steps
        stimuli_choices: What are the posible actions? 
        human_data
        seed
        """

        self.episode_steps = episode_steps
        self._reset_next_step = True
        self._action_history = []

        #Init WCST variables
        self.nb_dim = 3 
        self.nb_features = 4
        self.nb_templates = self.nb_features
        r = 3  #rules number, we have 3 rules

        self.nbTS = 0
        self.nb_win = 0
        self.t_criterion = 0
        self.t_err = 0
        self.criterions = []

        self.winstreak = 0
        self.m_percep = WCST.perception(self.nb_dim, self.nb_templates, self.nb_features)
        self.reasoning_list = []
        self.rule = 0

        #Last card info, it's dealt for the first time on reset method
        self.np_data = []
        self.v_data = []

    def new_card(self):
        v_data = [] #list type
        np_data = WCST.response_item_Reasoning(self.nb_dim, self.nb_features, self.m_percep, self.reasoning_list) #Modified WCST version
                
        #Transform into a vector
        for arr in np_data:
            for e in arr:
                v_data.append(e)

        #Save last card info
        self.np_data = np_data
        self.v_data = v_data

        return np_data, v_data

    def reset(self):
        self._reset_next_step = False
        self._current_step = 0
        self._action_history.clear()

        #Deal new card
        obs = self._observation()

        pass
        #return dm_env.restart(self._observation())

    def _episode_return(self):
      return 0.0

    def rule_switching(self, rule):
        """
        Serially changing the rules : color - form - number.
        """
        if rule!=2:
            rule = rule+1
        else:
            rule = 0
        return rule

    def external_feedback(self, action):
        """
        Returns a true reward according to the success or not of the card chosen.
        """
        response_card = self.np_data
        reference_cards = self.m_percep
        right_action_i = 0

        #print("Determine reward for rule:", self.rule, "and card: ")
        #print(response_card)

        for i in range(0, self.nb_templates):

            if np.array_equal(reference_cards[i][self.rule], response_card[self.rule]):
                right_action_i = i

        if right_action_i == action:
            #0 to decrease error activity
            return 0
        else: 
            #1 to activate error cluster
            return 1


    def step(self, action: int):

        if self._reset_next_step:
            return self.reset()

        agent_action = WCST_Env.ACTIONS[action]

        #Produce reward
        step_reward = self.external_feedback(agent_action)
        print("Reward:", step_reward)

        ##Winstreak count
        if step_reward == 0:
            self.t_err = 0
            self.nb_win += 1
            self.winstreak += 1
            #ptrial.append(1)
            #ntrial.append(0)

        if step_reward == 1:
            self.t_criterion += 1
            self.t_err += 1

            #FIXME: In the original code winstreak is reset
            #after a positive reward. This doesn't look right.

            #self.winstreak = 0
            #ptrial.append(0)
            #ntrial.append(1)

        # Criterion test
        # After 3 wins, then change the rule
        if self.winstreak==3:
            self.rule = self.rule_switching(self.rule)
            self.criterions.append(self.t_criterion)
            #Reset some variables and increment nbTS
            self.t_criterion = 0
            self.winstreak = 0
            self.nbTS +=1
            print("winstreak=3, New rule is ", self.rule, "NbTS=", self.nbTS)
        else:
            print("Winstreak=", self.winstreak)

        self._action_history.append(agent_action)
        self._current_step += 1

        # Check for termination.
        if self.nbTS >= 6:
            self._reset_next_step = True
            #return dm_env.termination(reward=self._episode_return(), observation=self._observation())
            print("Return last observation and terminate")
            pass
        else:
            #Send reward to agent and a new observation
            #Uncomment in notebook
            #return dm_env.transition(reward=step_reward, observation=self._observation())
            #Comment this one in notebook
            observation=self._observation()
            print("Return observation")
            pass
        
    def observation_spec(self):
        #return dm_env.specs.BoundedArray(
        #return (
        #    shape=self.stimuli.shape,
        #    dtype=self.stimuli.dtype,
        #    name='nback_stimuli', minimum=0, maximum=len(self.stimuli_choices) + 1
        #)
        pass

    def action_spec(self):
        #return dm_env.specs.DiscreteArray(
        #    num_values=len(NBack.ACTIONS),
        #    dtype=np.int32,
        #    name='action')
        pass

    def _observation(self):
        # agent observes only the current trial

        #INPUT new card, (Environment)
        np_data, card = self.new_card()

        #print("New card is np_data", np_data)
        #print("New card is v_data", card)
        obs = card
        return obs

    @staticmethod
    def create_environment():
        """Utility function to create a N-back environment and its spec."""

        # Make sure the environment outputs single-precision floats.
        #environment = wrappers.SinglePrecisionWrapper(NBack())

        # Grab the spec of the environment.
        #environment_spec = specs.make_environment_spec(environment)
        #return environment, environment_spec
        pass
  
## Test run
env = WCST_Env()

# First observation
timestep = env.reset()

import random

## FIXME: After 36 cards it stalls, 
# according to the rule it should end the game internally

for i in range(0,300):
    print("Step ", i)
    action = random.randint(0,2)
    env.step(action)
    
print("END")



