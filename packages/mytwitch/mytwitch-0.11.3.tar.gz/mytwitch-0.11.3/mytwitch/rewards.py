import yaml

from contextlib import suppress

from .auth import UserToken
from .request import APIRequest
from .exceptions import APIRequestError


class RewardManager:
    """Get, create, delete, and update custom rewards."""

    valid_body_parameters = {
        'title', 'prompt', 'cost', 'background_color',
        'is_enabled', 'is_user_input_required',
        'is_max_per_stream_enabled', 'max_per_stream',
        'is_max_per_user_per_stream_enabled', 'max_per_user_per_stream',
        'is_global_cooldown_enabled', 'global_cooldown_seconds',
        'is_paused', 'should_redemptions_skip_request_queue'
    }

    def __init__(self, token: UserToken):
        self.token = token

    def _create_reward(self, title: str, cost: int, **options):
        """Create a new reward on the channel."""

        if set(options.keys()).difference(self.valid_body_parameters):
            raise KeyError('Invalid keys provided for custom reward.')
        
        # Send a request for reward creation with the specified options
        
        response = APIRequest('POST',
            'https://api.twitch.tv/helix/channel_points/custom_rewards',
            
            params={
                'broadcaster_id': self.token.user_id,
            },
            headers={
                'Client-Id': self.token.client_id,
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
            },
            json={
                'title': title,
                'cost': cost,
                **options,
            },
        ).send()

        # Extract data, initialise reward object, and return it
        return Reward(self, response['data'][0])

    def _update_reward(self, reward_id: str, /, **options):
        """Update information about reward."""

        APIRequest('PATCH',
            'https://api.twitch.tv/helix/channel_points/custom_rewards',

            params={
                'broadcaster_id': self.token.user_id,
                'id': reward_id,
            },
            headers={
                'Client-Id': self.token.client_id,
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
            },
            json=options,
        )

    def _delete_reward(self, reward_id: str, /, *, ignore_not_found: bool = True):
        """Delete a reward from channel."""

        try:
            APIRequest('DELETE',
                'https://api.twitch.tv/helix/channel_points/custom_rewards',
                
                params={
                    'broadcaster_id': self.token.user_id,
                    'id': reward_id,
                },
                headers={
                    'Client-Id': self.token.client_id,
                    'Authorization': f'Bearer {self.token}',
                },
            ).send()

            return True
        
        except APIRequestError as e:
            if e.status == 404 and ignore_not_found:
                return False
            raise e

    def _get_rewards(self, reward_id: str = None, /, *, only_manageable_rewards: bool = True):
        """Get custom rewards from channel."""

        # Prepare parameters

        params = {
            'broadcaster_id': self.token.user_id,
            'only_manageable_rewards': only_manageable_rewards,
        }

        if reward_id is not None:
            params['id'] = reward_id


        # Send request

        response = APIRequest('GET',
            'https://api.twitch.tv/helix/channel_points/custom_rewards',

            params=params,
            headers={
                'Client-Id': self.token.client_id,
                'Authorization': f'Bearer {self.token}',
            },
        ).send()
        
        rewards = response['data']


        # Return only the matching reward if ID is provided
        if reward_id is not None:
            if not rewards:
                return None
            return Reward(self, rewards[0])

        # Otherwise, return full list of rewards
        return [Reward(self, reward) for reward in rewards]

    def add(self, title: str, cost: int, **options):
        """Safely add or get a custom reward."""

        try:
            return self._create_reward(title, cost, **options)
        
        except APIRequestError as e:
            if e.status == 400 and e.message == 'CREATE_CUSTOM_REWARD_DUPLICATE_REWARD':
                for reward in self._get_rewards():
                    if reward['title'] == title:
                        # If the provided options do not match with the existing reward,
                        # update the existing one to the new options
                        for key, value in options.items():
                            with suppress(IndexError, KeyError):
                                if reward[key] != value:
                                    reward.update(**options)
                                    break
                        return reward

                raise RuntimeError(
                    'Duplicate reward on channel but cannot be retrieved. '
                    'Something may have changed in-between requests. '
                    'This error is highly unlikely and should be solved by trying again.'
                ) from e
                
            raise e

    @property
    def available_slots(self):
        """Get how many more custom rewards can be added to the channel."""
        return 50 - len(self._get_rewards(only_manageable_rewards=False))


class Reward:
    def __init__(self, manager: RewardManager, data: dict):
        self.manager = manager
        self.data = data

    def __getitem__(self, key: int | str):
        return self.data[key]

    def update(self, **options):
        """Update information about reward."""
        self.manager._update_reward(self.data['id'], **options)

    def delete(self, *, ignore_not_found: bool = True):
        """Delete reward from channel."""
        return self.manager._delete_reward(
            self.data['id'], ignore_not_found=ignore_not_found)

    def refresh(self):
        """Refresh data to match the reward on the channel."""
        self.data = self.manager._get_rewards(self['id']).data


def load_rewards(path: str, token: UserToken):
    """Set up rewards from the parameters of a YAML configuration file.
    
    Example:

        Title of My First Reward:
            cost: 10
            prompt: Redeem a reward for the sake of it.
            color: "#3d3b34"

        Title of My Second Reward:
            cost: 15
            prompt: This is another reward you can redeem.
            color: "#23c48e"
    """

    rwm = RewardManager(token)

    with open(path, 'r') as f:
        for title, options in yaml.safe_load(f).items():
            if 'cost' not in options:
                raise ValueError(f'Cost is not defined for {title!r}.')

            yield rwm.add(title, options.pop('cost'), **options)