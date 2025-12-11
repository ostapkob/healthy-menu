
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```sh
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const SHELL: string;
	export const npm_command: string;
	export const separator_powerline_left: string;
	export const LSCOLORS: string;
	export const SESSION_MANAGER: string;
	export const NVIM_PLUGINS_PATH: string;
	export const npm_config_userconfig: string;
	export const COLORTERM: string;
	export const npm_config_cache: string;
	export const LESS: string;
	export const NVM_INC: string;
	export const HISTCONTROL: string;
	export const XDG_MENU_PREFIX: string;
	export const TERM_PROGRAM_VERSION: string;
	export const TMUX: string;
	export const HOSTNAME: string;
	export const HISTSIZE: string;
	export const _P9K_TTY: string;
	export const NODE: string;
	export const SSH_AUTH_SOCK: string;
	export const P9K_TTY: string;
	export const MEMORY_PRESSURE_WRITE: string;
	export const TMUX_PLUGIN_MANAGER_PATH: string;
	export const color_window_off_status_current_bg: string;
	export const COLOR: string;
	export const npm_config_local_prefix: string;
	export const SDKMAN_CANDIDATES_DIR: string;
	export const XMODIFIERS: string;
	export const DESKTOP_SESSION: string;
	export const yank: string;
	export const KITTY_PID: string;
	export const color_dark: string;
	export const npm_config_globalconfig: string;
	export const GPG_TTY: string;
	export const EDITOR: string;
	export const PWD: string;
	export const XDG_SESSION_DESKTOP: string;
	export const LOGNAME: string;
	export const XDG_SESSION_TYPE: string;
	export const wg_is_zoomed: string;
	export const npm_config_init_module: string;
	export const SYSTEMD_EXEC_PID: string;
	export const color_blue: string;
	export const wg_date: string;
	export const _: string;
	export const XAUTHORITY: string;
	export const KITTY_PUBLIC_KEY: string;
	export const color_window_off_indicator: string;
	export const ZSH_TMUX_CONFIG: string;
	export const CDPATH: string;
	export const color_black: string;
	export const GDM_LANG: string;
	export const color_green: string;
	export const HOME: string;
	export const USERNAME: string;
	export const SSH_ASKPASS: string;
	export const LANG: string;
	export const LS_COLORS: string;
	export const XDG_CURRENT_DESKTOP: string;
	export const npm_package_version: string;
	export const _ZSH_TMUX_FIXED_CONFIG: string;
	export const MEMORY_PRESSURE_WATCH: string;
	export const WAYLAND_DISPLAY: string;
	export const color_red: string;
	export const KITTY_WINDOW_ID: string;
	export const INVOCATION_ID: string;
	export const wg_is_keys_off: string;
	export const color_purple: string;
	export const GROOVY_HOME: string;
	export const MANAGERPID: string;
	export const color_session_text: string;
	export const color_level_warn: string;
	export const INIT_CWD: string;
	export const separator_powerline_right: string;
	export const npm_lifecycle_script: string;
	export const NVM_DIR: string;
	export const MOZ_GMP_PATH: string;
	export const GNOME_SETUP_DISPLAY: string;
	export const color_yellow: string;
	export const npm_config_npm_version: string;
	export const color_status_text: string;
	export const XDG_SESSION_CLASS: string;
	export const TERMINFO: string;
	export const TERM: string;
	export const npm_package_name: string;
	export const ZSH: string;
	export const npm_config_prefix: string;
	export const LESSOPEN: string;
	export const USER: string;
	export const TMUX_PANE: string;
	export const PASS: string;
	export const color_level_ok: string;
	export const color_light: string;
	export const CONDA_SHLVL: string;
	export const SDKMAN_DIR: string;
	export const DISPLAY: string;
	export const npm_lifecycle_event: string;
	export const SHLVL: string;
	export const NVM_CD_FLAGS: string;
	export const PAGER: string;
	export const QT_IM_MODULE: string;
	export const _P9K_SSH_TTY: string;
	export const SDKMAN_CANDIDATES_API: string;
	export const ATUIN_SESSION: string;
	export const npm_config_user_agent: string;
	export const wg_session: string;
	export const npm_execpath: string;
	export const ATUIN_HISTORY_ID: string;
	export const color_main: string;
	export const XDG_RUNTIME_DIR: string;
	export const ZSH_TMUX_TERM: string;
	export const color_white: string;
	export const DEBUGINFOD_URLS: string;
	export const npm_package_json: string;
	export const color_level_stress: string;
	export const DEBUGINFOD_IMA_CERT_PATH: string;
	export const color_black_light: string;
	export const P9K_SSH: string;
	export const KDEDIRS: string;
	export const JOURNAL_STREAM: string;
	export const XDG_DATA_DIRS: string;
	export const color_secondary: string;
	export const npm_config_noproxy: string;
	export const PATH: string;
	export const npm_config_node_gyp: string;
	export const GDMSESSION: string;
	export const wg_battery: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const SDKMAN_PLATFORM: string;
	export const npm_config_global_prefix: string;
	export const tmux_version: string;
	export const NVM_BIN: string;
	export const MAIL: string;
	export const wg_user_host: string;
	export const ENVMAN_LOAD: string;
	export const KITTY_INSTALLATION_DIR: string;
	export const GIO_LAUNCHED_DESKTOP_FILE_PID: string;
	export const npm_node_execpath: string;
	export const npm_config_engine_strict: string;
	export const color_window_off_status_bg: string;
	export const OLDPWD: string;
	export const color_orange: string;
	export const TERM_PROGRAM: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		SHELL: string;
		npm_command: string;
		separator_powerline_left: string;
		LSCOLORS: string;
		SESSION_MANAGER: string;
		NVIM_PLUGINS_PATH: string;
		npm_config_userconfig: string;
		COLORTERM: string;
		npm_config_cache: string;
		LESS: string;
		NVM_INC: string;
		HISTCONTROL: string;
		XDG_MENU_PREFIX: string;
		TERM_PROGRAM_VERSION: string;
		TMUX: string;
		HOSTNAME: string;
		HISTSIZE: string;
		_P9K_TTY: string;
		NODE: string;
		SSH_AUTH_SOCK: string;
		P9K_TTY: string;
		MEMORY_PRESSURE_WRITE: string;
		TMUX_PLUGIN_MANAGER_PATH: string;
		color_window_off_status_current_bg: string;
		COLOR: string;
		npm_config_local_prefix: string;
		SDKMAN_CANDIDATES_DIR: string;
		XMODIFIERS: string;
		DESKTOP_SESSION: string;
		yank: string;
		KITTY_PID: string;
		color_dark: string;
		npm_config_globalconfig: string;
		GPG_TTY: string;
		EDITOR: string;
		PWD: string;
		XDG_SESSION_DESKTOP: string;
		LOGNAME: string;
		XDG_SESSION_TYPE: string;
		wg_is_zoomed: string;
		npm_config_init_module: string;
		SYSTEMD_EXEC_PID: string;
		color_blue: string;
		wg_date: string;
		_: string;
		XAUTHORITY: string;
		KITTY_PUBLIC_KEY: string;
		color_window_off_indicator: string;
		ZSH_TMUX_CONFIG: string;
		CDPATH: string;
		color_black: string;
		GDM_LANG: string;
		color_green: string;
		HOME: string;
		USERNAME: string;
		SSH_ASKPASS: string;
		LANG: string;
		LS_COLORS: string;
		XDG_CURRENT_DESKTOP: string;
		npm_package_version: string;
		_ZSH_TMUX_FIXED_CONFIG: string;
		MEMORY_PRESSURE_WATCH: string;
		WAYLAND_DISPLAY: string;
		color_red: string;
		KITTY_WINDOW_ID: string;
		INVOCATION_ID: string;
		wg_is_keys_off: string;
		color_purple: string;
		GROOVY_HOME: string;
		MANAGERPID: string;
		color_session_text: string;
		color_level_warn: string;
		INIT_CWD: string;
		separator_powerline_right: string;
		npm_lifecycle_script: string;
		NVM_DIR: string;
		MOZ_GMP_PATH: string;
		GNOME_SETUP_DISPLAY: string;
		color_yellow: string;
		npm_config_npm_version: string;
		color_status_text: string;
		XDG_SESSION_CLASS: string;
		TERMINFO: string;
		TERM: string;
		npm_package_name: string;
		ZSH: string;
		npm_config_prefix: string;
		LESSOPEN: string;
		USER: string;
		TMUX_PANE: string;
		PASS: string;
		color_level_ok: string;
		color_light: string;
		CONDA_SHLVL: string;
		SDKMAN_DIR: string;
		DISPLAY: string;
		npm_lifecycle_event: string;
		SHLVL: string;
		NVM_CD_FLAGS: string;
		PAGER: string;
		QT_IM_MODULE: string;
		_P9K_SSH_TTY: string;
		SDKMAN_CANDIDATES_API: string;
		ATUIN_SESSION: string;
		npm_config_user_agent: string;
		wg_session: string;
		npm_execpath: string;
		ATUIN_HISTORY_ID: string;
		color_main: string;
		XDG_RUNTIME_DIR: string;
		ZSH_TMUX_TERM: string;
		color_white: string;
		DEBUGINFOD_URLS: string;
		npm_package_json: string;
		color_level_stress: string;
		DEBUGINFOD_IMA_CERT_PATH: string;
		color_black_light: string;
		P9K_SSH: string;
		KDEDIRS: string;
		JOURNAL_STREAM: string;
		XDG_DATA_DIRS: string;
		color_secondary: string;
		npm_config_noproxy: string;
		PATH: string;
		npm_config_node_gyp: string;
		GDMSESSION: string;
		wg_battery: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		SDKMAN_PLATFORM: string;
		npm_config_global_prefix: string;
		tmux_version: string;
		NVM_BIN: string;
		MAIL: string;
		wg_user_host: string;
		ENVMAN_LOAD: string;
		KITTY_INSTALLATION_DIR: string;
		GIO_LAUNCHED_DESKTOP_FILE_PID: string;
		npm_node_execpath: string;
		npm_config_engine_strict: string;
		color_window_off_status_bg: string;
		OLDPWD: string;
		color_orange: string;
		TERM_PROGRAM: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
