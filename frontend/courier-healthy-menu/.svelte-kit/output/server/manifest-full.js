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
		client: {start:"_app/immutable/entry/start.DZ-ohw7_.js",app:"_app/immutable/entry/app.BeS78BiV.js",imports:["_app/immutable/entry/start.DZ-ohw7_.js","_app/immutable/chunks/DHq-bfiu.js","_app/immutable/chunks/sF-5qWL7.js","_app/immutable/chunks/C7ffHk-_.js","_app/immutable/chunks/D70PosjZ.js","_app/immutable/entry/app.BeS78BiV.js","_app/immutable/chunks/sF-5qWL7.js","_app/immutable/chunks/DkO8GDoS.js","_app/immutable/chunks/Dexp1yiY.js","_app/immutable/chunks/D70PosjZ.js","_app/immutable/chunks/DP6b_pEU.js","_app/immutable/chunks/mjQeaoyB.js","_app/immutable/chunks/C7ffHk-_.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js'))
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
				id: "/couriers",
				pattern: /^\/couriers\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/my-deliveries",
				pattern: /^\/my-deliveries\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/orders",
				pattern: /^\/orders\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
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
