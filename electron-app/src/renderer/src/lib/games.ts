export interface PortDef {
  port: number
  protocol: 'TCP' | 'UDP' | 'TCP/UDP'
  description: string
}

export interface SettingDef {
  key: string
  label: string
  type: 'string' | 'password' | 'int' | 'bool' | 'choice'
  default: string | number | boolean
  required?: boolean
  placeholder?: string
  min?: number
  max?: number
  options?: string[]
  helpUrl?: string
  tooltip?: string
}

export interface Game {
  id: string
  name: string
  description: string
  genre: string
  platforms: string[]
  steamAppId: string
  installMode: 'steam' | 'mojang'
  launchMode: 'steam' | 'java' | 'dst_dual_shard'
  serverDirName: string
  executable: string
  executableSubdir: string
  launchArgs: string
  processNames: string[]
  defaultPort: number
  ports: PortDef[]
  serverSettings: SettingDef[]
  bannerColor: string
  accentColor: string
  installSteps?: string[]  // custom labels for the 3-step install wizard
}

export const GAMES: Game[] = [
  {
    id: 'palworld',
    name: 'Palworld',
    description: 'Open-world survival crafting game with creature collection and base building.',
    genre: 'Survival / Crafting',
    platforms: ['Windows'],
    steamAppId: '2394010',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'PalServer',
    executable: 'PalServer.exe',
    executableSubdir: '',
    launchArgs: '-port={port} -players={max_players} -useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS',
    processNames: ['PalServer.exe', 'PalServer-Win64-Test-Cmd.exe'],
    defaultPort: 8211,
    ports: [
      { port: 8211, protocol: 'UDP', description: 'Game' },
      { port: 27015, protocol: 'UDP', description: 'Steam' }
    ],
    bannerColor: 'from-emerald-900 to-teal-950',
    accentColor: '#10b981',
    serverSettings: [
      { key: 'port', label: 'Server Port', type: 'int', default: 8211, min: 1024, max: 65535 },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 32, min: 1, max: 32 },
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Palworld Server', placeholder: 'Server Name' },
      { key: 'server_password', label: 'Server Password', type: 'password', default: '', placeholder: 'Leave blank for public' },
      { key: 'admin_password', label: 'Admin Password', type: 'password', default: '', required: true }
    ]
  },
  {
    id: 'valheim',
    name: 'Valheim',
    description: 'Viking survival game with Norse mythology, exploration, and brutal combat.',
    genre: 'Survival / RPG',
    platforms: ['Windows', 'Linux'],
    steamAppId: '896660',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'valheim_dedicated_server',
    executable: 'valheim_dedicated_server.exe',
    executableSubdir: '',
    launchArgs: '-nographics -batchmode -name "{server_name}" -port {port} -world "{world_name}" -password "{password}" -public {public}',
    processNames: ['valheim_dedicated_server.exe', 'valheim_server'],
    defaultPort: 2456,
    ports: [
      { port: 2456, protocol: 'UDP', description: 'Game' },
      { port: 2457, protocol: 'UDP', description: 'Query' }
    ],
    bannerColor: 'from-blue-950 to-indigo-950',
    accentColor: '#6366f1',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Valheim Server', required: true },
      { key: 'world_name', label: 'World Name', type: 'string', default: 'Dedicated', required: true },
      { key: 'port', label: 'Port', type: 'int', default: 2456, min: 1024, max: 65535 },
      { key: 'password', label: 'Password', type: 'password', default: '', placeholder: 'Min 5 chars if set' },
      { key: 'public', label: 'Public Server', type: 'bool', default: true }
    ]
  },
  {
    id: 'rust',
    name: 'Rust',
    description: 'Harsh multiplayer survival game where players fight for resources and dominance.',
    genre: 'Survival / PvP',
    platforms: ['Windows', 'Linux'],
    steamAppId: '258550',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'rust_dedicated_server',
    executable: 'RustDedicated.exe',
    executableSubdir: '',
    launchArgs: '-batchmode +server.port {port} +server.hostname "{server_name}" +server.maxplayers {max_players} +server.worldsize {world_size} +server.seed {seed} +rcon.port {rcon_port} +rcon.password "{rcon_password}" +rcon.web 1',
    processNames: ['RustDedicated.exe', 'RustDedicated'],
    defaultPort: 28015,
    ports: [
      { port: 28015, protocol: 'UDP', description: 'Game' },
      { port: 28016, protocol: 'TCP', description: 'RCON' }
    ],
    bannerColor: 'from-orange-950 to-red-950',
    accentColor: '#f97316',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Rust Server', required: true },
      { key: 'port', label: 'Game Port', type: 'int', default: 28015, min: 1024, max: 65535 },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 50, min: 1, max: 500 },
      { key: 'world_size', label: 'World Size', type: 'choice', default: '3500', options: ['2000', '3500', '4000', '6000'] },
      { key: 'seed', label: 'World Seed', type: 'int', default: 12345, min: 0, max: 2147483647 },
      { key: 'rcon_port', label: 'RCON Port', type: 'int', default: 28016, min: 1024, max: 65535 },
      { key: 'rcon_password', label: 'RCON Password', type: 'password', default: '', required: true }
    ]
  },
  {
    id: 'dst',
    name: "Don't Starve Together",
    description: 'Uncompromising wilderness survival game with friends in a dark and whimsical world.',
    genre: 'Survival',
    platforms: ['Windows', 'Linux'],
    steamAppId: '343050',
    installMode: 'steam',
    launchMode: 'dst_dual_shard',
    serverDirName: 'DST_Dedicated',
    executable: 'dontstarve_dedicated_server_nullrenderer_x64.exe',
    executableSubdir: 'bin64',
    launchArgs: '',
    processNames: ['dontstarve_dedicated_server_nullrenderer_x64.exe'],
    defaultPort: 10999,
    ports: [
      { port: 10999, protocol: 'UDP', description: 'Master' },
      { port: 11000, protocol: 'UDP', description: 'Caves' }
    ],
    bannerColor: 'from-yellow-950 to-amber-950',
    accentColor: '#eab308',
    serverSettings: [
      { key: 'server_name', label: 'Cluster Name', type: 'string', default: 'My DST Server', required: true },
      { key: 'server_description', label: 'Description', type: 'string', default: '' },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 6, min: 1, max: 64 },
      { key: 'game_mode', label: 'Game Mode', type: 'choice', default: 'survival', options: ['survival', 'endless', 'wilderness'] },
      { key: 'password', label: 'Password', type: 'password', default: '' },
      { key: 'pvp', label: 'PvP Enabled', type: 'bool', default: false },
      { key: 'server_token', label: 'Cluster Token', type: 'password', default: '', required: true, helpUrl: 'https://accounts.klei.com/account/game/servers' }
    ]
  },
  {
    id: 'minecraft',
    name: 'Minecraft',
    description: 'The iconic sandbox survival game. Build, explore, and survive in an infinite procedurally generated world.',
    genre: 'Sandbox / Survival',
    platforms: ['Windows', 'Linux', 'macOS'],
    steamAppId: '',
    installMode: 'mojang',
    launchMode: 'java',
    serverDirName: 'minecraft_server',
    executable: 'server.jar',
    executableSubdir: '',
    launchArgs: '-Xmx{max_memory}G -Xms{min_memory}G -jar server.jar nogui',
    processNames: ['java'],
    defaultPort: 25565,
    ports: [
      { port: 25565, protocol: 'TCP', description: 'Game' },
      { port: 25575, protocol: 'TCP', description: 'RCON' }
    ],
    bannerColor: 'from-green-950 to-stone-950',
    accentColor: '#22c55e',
    installSteps: ['Check Java & fetch version', 'Download server JAR', 'Configure & finalize'],
    serverSettings: [
      { key: 'port', label: 'Server Port', type: 'int', default: 25565, min: 1024, max: 65535 },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 20, min: 1, max: 1000 },
      { key: 'motd', label: 'Server Description (MOTD)', type: 'string', default: 'A Minecraft Server', placeholder: 'Shown in the server list' },
      { key: 'difficulty', label: 'Difficulty', type: 'choice', default: 'normal', options: ['peaceful', 'easy', 'normal', 'hard'] },
      { key: 'gamemode', label: 'Default Gamemode', type: 'choice', default: 'survival', options: ['survival', 'creative', 'adventure', 'spectator'] },
      { key: 'max_memory', label: 'Max RAM (GB)', type: 'int', default: 4, min: 1, max: 64 },
      { key: 'min_memory', label: 'Min RAM (GB)', type: 'int', default: 2, min: 1, max: 64 },
      { key: 'whitelist', label: 'Whitelist Only', type: 'bool', default: false },
      { key: 'pvp', label: 'PvP Enabled', type: 'bool', default: true },
      { key: 'online_mode', label: 'Online Mode (auth)', type: 'bool', default: true, tooltip: 'Disable only for offline/LAN play' },
      { key: 'rcon_password', label: 'RCON Password', type: 'password', default: '', placeholder: 'Leave blank to disable RCON' },
      { key: 'rcon_port', label: 'RCON Port', type: 'int', default: 25575, min: 1024, max: 65535 }
    ]
  }
]
