export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["robots.txt"]),
	mimeTypes: {".txt":"text/plain"},
	_: {
		client: {start:"_app/immutable/entry/start.DTyC5OYk.js",app:"_app/immutable/entry/app.COhKX7st.js",imports:["_app/immutable/entry/start.DTyC5OYk.js","_app/immutable/chunks/DMqPOJMS.js","_app/immutable/chunks/wShWkVpQ.js","_app/immutable/chunks/BTDDw6Y7.js","_app/immutable/chunks/uyRXS268.js","_app/immutable/entry/app.COhKX7st.js","_app/immutable/chunks/wShWkVpQ.js","_app/immutable/chunks/DtUbhPAe.js","_app/immutable/chunks/CJeTjUBQ.js","_app/immutable/chunks/uyRXS268.js","_app/immutable/chunks/BWFvfl_G.js","_app/immutable/chunks/BkLtfsHd.js","_app/immutable/chunks/BTDDw6Y7.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/cart",
				pattern: /^\/cart\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/orders",
				pattern: /^\/orders\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
