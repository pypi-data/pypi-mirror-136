var _JUPYTERLAB;(()=>{"use strict";var e,r,t={869:(e,r,t)=>{var a={"./index":()=>t.e(568).then((()=>()=>t(568))),"./extension":()=>t.e(568).then((()=>()=>t(568))),"./style":()=>t.e(747).then((()=>()=>t(747)))},o=(e,r)=>(t.R=r,r=t.o(a,e)?a[e]():Promise.resolve().then((()=>{throw new Error('Module "'+e+'" does not exist in container.')})),t.R=void 0,r),n=(e,r)=>{if(t.S){var a="default",o=t.S[a];if(o&&o!==e)throw new Error("Container initialization failed as it has already been initialized with a different share scope");return t.S[a]=e,t.I(a,r)}};t.d(r,{get:()=>o,init:()=>n})}},a={};function o(e){var r=a[e];if(void 0!==r)return r.exports;var n=a[e]={id:e,exports:{}};return t[e](n,n.exports,o),n.exports}o.m=t,o.c=a,o.n=e=>{var r=e&&e.__esModule?()=>e.default:()=>e;return o.d(r,{a:r}),r},o.d=(e,r)=>{for(var t in r)o.o(r,t)&&!o.o(e,t)&&Object.defineProperty(e,t,{enumerable:!0,get:r[t]})},o.f={},o.e=e=>Promise.all(Object.keys(o.f).reduce(((r,t)=>(o.f[t](e,r),r)),[])),o.u=e=>e+"."+{568:"34c32434ba86a64313a5",747:"d3ecdbd2daa351ab2b15"}[e]+".js?v="+{568:"34c32434ba86a64313a5",747:"d3ecdbd2daa351ab2b15"}[e],o.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"==typeof window)return window}}(),o.o=(e,r)=>Object.prototype.hasOwnProperty.call(e,r),e={},r="jupyterlab_cfps_preload:",o.l=(t,a,n,i)=>{if(e[t])e[t].push(a);else{var l,d;if(void 0!==n)for(var u=document.getElementsByTagName("script"),s=0;s<u.length;s++){var p=u[s];if(p.getAttribute("src")==t||p.getAttribute("data-webpack")==r+n){l=p;break}}l||(d=!0,(l=document.createElement("script")).charset="utf-8",l.timeout=120,o.nc&&l.setAttribute("nonce",o.nc),l.setAttribute("data-webpack",r+n),l.src=t),e[t]=[a];var f=(r,a)=>{l.onerror=l.onload=null,clearTimeout(c);var o=e[t];if(delete e[t],l.parentNode&&l.parentNode.removeChild(l),o&&o.forEach((e=>e(a))),r)return r(a)},c=setTimeout(f.bind(null,void 0,{type:"timeout",target:l}),12e4);l.onerror=f.bind(null,l.onerror),l.onload=f.bind(null,l.onload),d&&document.head.appendChild(l)}},o.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},(()=>{o.S={};var e={},r={};o.I=(t,a)=>{a||(a=[]);var n=r[t];if(n||(n=r[t]={}),!(a.indexOf(n)>=0)){if(a.push(n),e[t])return e[t];o.o(o.S,t)||(o.S[t]={});var i=o.S[t],l="jupyterlab_cfps_preload",d=[];return"default"===t&&((e,r,t,a)=>{var n=i[e]=i[e]||{},d=n[r];(!d||!d.loaded&&(1!=!d.eager?a:l>d.from))&&(n[r]={get:()=>o.e(568).then((()=>()=>o(568))),from:l,eager:!1})})("jupyterlab_cfps_preload","0.3.1"),e[t]=d.length?Promise.all(d).then((()=>e[t]=1)):1}}})(),(()=>{var e;o.g.importScripts&&(e=o.g.location+"");var r=o.g.document;if(!e&&r&&(r.currentScript&&(e=r.currentScript.src),!e)){var t=r.getElementsByTagName("script");t.length&&(e=t[t.length-1].src)}if(!e)throw new Error("Automatic publicPath is not supported in this browser");e=e.replace(/#.*$/,"").replace(/\?.*$/,"").replace(/\/[^\/]+$/,"/"),o.p=e})(),(()=>{var e={111:0};o.f.j=(r,t)=>{var a=o.o(e,r)?e[r]:void 0;if(0!==a)if(a)t.push(a[2]);else{var n=new Promise(((t,o)=>a=e[r]=[t,o]));t.push(a[2]=n);var i=o.p+o.u(r),l=new Error;o.l(i,(t=>{if(o.o(e,r)&&(0!==(a=e[r])&&(e[r]=void 0),a)){var n=t&&("load"===t.type?"missing":t.type),i=t&&t.target&&t.target.src;l.message="Loading chunk "+r+" failed.\n("+n+": "+i+")",l.name="ChunkLoadError",l.type=n,l.request=i,a[1](l)}}),"chunk-"+r,r)}};var r=(r,t)=>{var a,n,[i,l,d]=t,u=0;if(i.some((r=>0!==e[r]))){for(a in l)o.o(l,a)&&(o.m[a]=l[a]);d&&d(o)}for(r&&r(t);u<i.length;u++)n=i[u],o.o(e,n)&&e[n]&&e[n][0](),e[n]=0},t=self.webpackChunkjupyterlab_cfps_preload=self.webpackChunkjupyterlab_cfps_preload||[];t.forEach(r.bind(null,0)),t.push=r.bind(null,t.push.bind(t))})();var n=o(869);(_JUPYTERLAB=void 0===_JUPYTERLAB?{}:_JUPYTERLAB).jupyterlab_cfps_preload=n})();