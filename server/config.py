import os

#TEAMS = ['cybersecnatlab', 'albania', 'australia', 'austria', 'belgium', 'bulgaria', 'canada', 'chile', 'costa-rica', 'croatia', 'cyprus', 'czech', 'denmark', 'estonia', 'finland', 'france', 'georgia', 'germany', 'greece', 'hungary', 'iceland', 'ireland', 'italy', 'kosovo', 'latvia', 'liechtenstein', 'luxembourg', 'malta', 'netherlands', 'norway', 'poland', 'portugal', 'romania', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'usa', 'cyprus2', 'denmark2', 'usa2', ]
TEAMS = ["cybersecnatlab", "europe", "albania", "austria", "belgium", "bulgaria", "croatia", "cyprus", "czech", "denmark", "estonia", "finland", "france", "georgia", "germany", "greece", "hungary", "iceland", "ireland", "italy", "latvia", "liechtenstein", "luxembourg", "malta", "netherlands", "norway", "poland", "portugal", "romania", "serbia", "slovakia", "slovenia", "spain", "sweden", "switzerland"]

CONFIG = {
    # Don't forget to remove the old database (flags.sqlite) before each competition.

    # The clients will run sploits on TEAMS and
    # fetch FLAG_FORMAT from sploits' stdout.
    'TEAMS': {TEAMS[i-1]: '10.62.{}.1'.format(i)
              for i in range(1, len(TEAMS) + 1)},
    'FLAG_FORMAT': r'[A-Z0-9]{31}=',

    # This configures how and where to submit flags.
    # The protocol must be a module in protocols/ directory.

    'SYSTEM_TOKEN':'12ad1db9850dc371b36f9f105661f47c',
    'SYSTEM_PROTOCOL': 'ecsc24_http',
    'SYSTEM_URL': 'http://10.10.0.1:8080/flags',
    'SYSTEM_PORT': 8080,

    'STRATEGY_ENDPOINT' : 'http://api:8000/strategy/teams/'

    # 'SYSTEM_PROTOCOL': 'ructf_http',
    # 'SYSTEM_URL': 'http://monitor.ructfe.org/flags',
    # 'SYSTEM_TOKEN': 'your_secret_token',

    # 'SYSTEM_PROTOCOL': 'volgactf',
    # 'SYSTEM_HOST': '127.0.0.1',

    # 'SYSTEM_PROTOCOL': 'forcad_tcp',
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,
    # 'TEAM_TOKEN': 'your_secret_token',

    # The server will submit not more than SUBMIT_FLAG_LIMIT flags
    # every SUBMIT_PERIOD seconds. Flags received more than
    # FLAG_LIFETIME seconds ago will be skipped.
    'SUBMIT_FLAG_LIMIT': 50,
    'SUBMIT_PERIOD': 5,
    'FLAG_LIFETIME': 5 * 60,

    # Password for the web interface. You can use it with any login.
    # This value will be excluded from the config before sending it to farm clients.
    'SERVER_PASSWORD': '1234',

    # Use authorization for API requests
    'ENABLE_API_AUTH': True,
    'API_TOKEN': os.environ.get('FARM_TOKEN')
}
