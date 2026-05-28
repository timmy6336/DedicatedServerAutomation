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
  installSteps?: string[]
  modsSubdir?: string       // path relative to instance dir where mod files are placed
  modExtensions?: string[]  // accepted file extensions shown in picker / drop zone
  modsNote?: string         // optional caveat shown in the Mods panel header
}

const DISCORD_WEBHOOK_SETTING: SettingDef = {
  key: 'discord_webhook',
  label: 'Discord Webhook URL',
  type: 'string',
  default: '',
  placeholder: 'https://discord.com/api/webhooks/…',
  tooltip: 'Post server start/stop notifications to a Discord channel'
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
    modsSubdir: 'Pal/Content/Paks',
    modExtensions: ['pak'],
    serverSettings: [
      { key: 'port', label: 'Server Port', type: 'int', default: 8211, min: 1024, max: 65535 },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 32, min: 1, max: 32 },
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Palworld Server', placeholder: 'Server Name' },
      { key: 'server_password', label: 'Server Password', type: 'password', default: '', placeholder: 'Leave blank for public' },
      { key: 'admin_password', label: 'Admin Password', type: 'password', default: '', required: true },
      DISCORD_WEBHOOK_SETTING
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
    modsSubdir: 'BepInEx/plugins',
    modExtensions: ['dll', 'zip'],
    modsNote: 'Requires BepInEx installed in the server directory first.',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Valheim Server', required: true },
      { key: 'world_name', label: 'World Name', type: 'string', default: 'Dedicated', required: true },
      { key: 'port', label: 'Port', type: 'int', default: 2456, min: 1024, max: 65535 },
      { key: 'password', label: 'Password', type: 'password', default: '', placeholder: 'Min 5 chars if set' },
      { key: 'public', label: 'Public Server', type: 'bool', default: true },
      DISCORD_WEBHOOK_SETTING
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
    modsSubdir: 'oxide/plugins',
    modExtensions: ['dll', 'cs'],
    modsNote: 'Requires Oxide/uMod installed in the server directory first.',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Rust Server', required: true },
      { key: 'port', label: 'Game Port', type: 'int', default: 28015, min: 1024, max: 65535 },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 50, min: 1, max: 500 },
      { key: 'world_size', label: 'World Size', type: 'choice', default: '3500', options: ['2000', '3500', '4000', '6000'] },
      { key: 'seed', label: 'World Seed', type: 'int', default: 12345, min: 0, max: 2147483647 },
      { key: 'rcon_port', label: 'RCON Port', type: 'int', default: 28016, min: 1024, max: 65535 },
      { key: 'rcon_password', label: 'RCON Password', type: 'password', default: '', required: true },
      DISCORD_WEBHOOK_SETTING
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
      { key: 'server_token', label: 'Cluster Token', type: 'password', default: '', required: true, helpUrl: 'https://accounts.klei.com/account/game/servers' },
      DISCORD_WEBHOOK_SETTING
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
    modsSubdir: 'mods',
    modExtensions: ['jar'],
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
      { key: 'rcon_port', label: 'RCON Port', type: 'int', default: 25575, min: 1024, max: 65535 },
      DISCORD_WEBHOOK_SETTING
    ]
  },
  {
    id: 'ark',
    name: 'ARK: Survival Evolved',
    description: 'Open-world survival game with dinosaurs. Tame creatures, build bases, and explore a prehistoric landscape.',
    genre: 'Survival / Action',
    platforms: ['Windows', 'Linux'],
    steamAppId: '376030',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'ark_server',
    executable: 'ShooterGameServer.exe',
    executableSubdir: 'ShooterGame/Binaries/Win64',
    launchArgs: 'TheIsland?listen?SessionName={server_name}?ServerPassword={password}?ServerAdminPassword={admin_password}?MaxPlayers={max_players}?Port={port}?QueryPort={query_port}',
    processNames: ['ShooterGameServer.exe', 'ShooterGameServer'],
    defaultPort: 7777,
    ports: [
      { port: 7777, protocol: 'UDP', description: 'Game' },
      { port: 7778, protocol: 'UDP', description: 'Raw UDP' },
      { port: 27015, protocol: 'UDP', description: 'Steam Query' }
    ],
    bannerColor: 'from-amber-950 to-stone-950',
    accentColor: '#d97706',
    serverSettings: [
      { key: 'server_name', label: 'Session Name', type: 'string', default: 'My ARK Server', required: true },
      { key: 'password', label: 'Join Password', type: 'password', default: '', placeholder: 'Leave blank for public' },
      { key: 'admin_password', label: 'Admin Password', type: 'password', default: 'changeme', required: true },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 70, min: 1, max: 255 },
      { key: 'port', label: 'Game Port', type: 'int', default: 7777, min: 1024, max: 65535 },
      { key: 'query_port', label: 'Query Port', type: 'int', default: 27015, min: 1024, max: 65535 },
      DISCORD_WEBHOOK_SETTING
    ]
  },
  {
    id: 'sevendays',
    name: '7 Days to Die',
    description: 'Open-world survival horror combining first-person shooter, tower defense, and RPG elements in a zombie apocalypse.',
    genre: 'Survival / Horror',
    platforms: ['Windows', 'Linux'],
    steamAppId: '294420',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: '7dtd_server',
    executable: '7DaysToDieServer.exe',
    executableSubdir: '',
    launchArgs: '-configfile=serverconfig.xml',
    processNames: ['7DaysToDieServer.exe', '7DaysToDieServer'],
    defaultPort: 26900,
    ports: [
      { port: 26900, protocol: 'UDP', description: 'Game' },
      { port: 26901, protocol: 'UDP', description: 'Query' },
      { port: 26902, protocol: 'UDP', description: 'Steam' },
      { port: 8080, protocol: 'TCP', description: 'Web Panel' }
    ],
    bannerColor: 'from-red-950 to-zinc-950',
    accentColor: '#ef4444',
    modsSubdir: 'Mods',
    modExtensions: ['dll', 'zip'],
    modsNote: 'Each mod must be a folder inside Mods/ containing ModInfo.xml. Drop the mod zip here and extract it manually.',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My 7DTD Server', required: true },
      { key: 'server_password', label: 'Server Password', type: 'password', default: '' },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 8, min: 1, max: 16 },
      { key: 'port', label: 'Server Port', type: 'int', default: 26900, min: 1024, max: 65535 },
      {
        key: 'difficulty', label: 'Difficulty', type: 'choice', default: 'Nomad',
        options: ['Scavenger', 'Adventurer', 'Nomad', 'Warrior', 'Survivalist', 'Insane']
      },
      DISCORD_WEBHOOK_SETTING
    ]
  },
  {
    id: 'zomboid',
    name: 'Project Zomboid',
    description: 'Deeply detailed isometric zombie survival with crafting, base-building, and NPCs in a persistent world.',
    genre: 'Survival / Horror',
    platforms: ['Windows', 'Linux'],
    steamAppId: '380870',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'zomboid_server',
    executable: 'ProjectZomboidServer.exe',
    executableSubdir: '',
    launchArgs: '-servername {server_name} -adminpassword {admin_password} -port {port}',
    processNames: ['ProjectZomboidServer.exe', 'java'],
    defaultPort: 16261,
    ports: [
      { port: 16261, protocol: 'UDP', description: 'Game' },
      { port: 16262, protocol: 'UDP', description: 'Direct' }
    ],
    bannerColor: 'from-zinc-900 to-neutral-950',
    accentColor: '#71717a',
    modsSubdir: 'Mods',
    modExtensions: ['zip'],
    modsNote: 'Project Zomboid mods are typically managed via Steam Workshop. File-drop places zips into the Mods/ folder.',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'pzserver', required: true },
      { key: 'admin_password', label: 'Admin Password', type: 'password', default: '', required: true },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 32, min: 1, max: 100 },
      { key: 'port', label: 'Server Port', type: 'int', default: 16261, min: 1024, max: 65535 },
      { key: 'public', label: 'Public Server', type: 'bool', default: false },
      DISCORD_WEBHOOK_SETTING
    ]
  },
  {
    id: 'vrising',
    name: 'V Rising',
    description: 'Vampire survival game with castle-building, crafting, and cooperative multiplayer in a gothic world.',
    genre: 'Survival / Action RPG',
    platforms: ['Windows'],
    steamAppId: '1829350',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'vrising_server',
    executable: 'VRisingServer.exe',
    executableSubdir: '',
    launchArgs: '-persistentDataPath .\\SaveData -serverName "{server_name}" -gamePort {port} -queryPort {query_port} -maxConnectedUsers {max_players}',
    processNames: ['VRisingServer.exe'],
    defaultPort: 9876,
    ports: [
      { port: 9876, protocol: 'UDP', description: 'Game' },
      { port: 9877, protocol: 'UDP', description: 'Query' }
    ],
    bannerColor: 'from-purple-950 to-rose-950',
    accentColor: '#a855f7',
    modsSubdir: 'BepInEx/plugins',
    modExtensions: ['dll', 'zip'],
    modsNote: 'Requires BepInEx installed in the server directory first.',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My V Rising Server', required: true },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 40, min: 1, max: 40 },
      { key: 'port', label: 'Game Port', type: 'int', default: 9876, min: 1024, max: 65535 },
      { key: 'query_port', label: 'Query Port', type: 'int', default: 9877, min: 1024, max: 65535 },
      DISCORD_WEBHOOK_SETTING
    ]
  },
  {
    id: 'enshrouded',
    name: 'Enshrouded',
    description: 'Survival action RPG set in a voxel world. Build, craft, and battle across a vast landscape with friends.',
    genre: 'Survival / Action RPG',
    platforms: ['Windows'],
    steamAppId: '2278520',
    installMode: 'steam',
    launchMode: 'steam',
    serverDirName: 'enshrouded_server',
    executable: 'enshrouded_server.exe',
    executableSubdir: '',
    launchArgs: '',
    processNames: ['enshrouded_server.exe'],
    defaultPort: 15636,
    ports: [
      { port: 15636, protocol: 'UDP', description: 'Game' },
      { port: 15637, protocol: 'UDP', description: 'Query' }
    ],
    bannerColor: 'from-violet-950 to-slate-950',
    accentColor: '#7c3aed',
    serverSettings: [
      { key: 'server_name', label: 'Server Name', type: 'string', default: 'My Enshrouded Server', required: true },
      { key: 'password', label: 'Server Password', type: 'password', default: '' },
      { key: 'max_players', label: 'Max Players', type: 'int', default: 16, min: 1, max: 16 },
      { key: 'port', label: 'Game Port', type: 'int', default: 15636, min: 1024, max: 65535 },
      DISCORD_WEBHOOK_SETTING
    ]
  }
]
