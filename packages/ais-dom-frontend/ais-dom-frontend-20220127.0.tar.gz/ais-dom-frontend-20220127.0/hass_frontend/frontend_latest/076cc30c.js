/*! For license information please see 076cc30c.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[2315],{14166:(t,e,n)=>{n.d(e,{W:()=>r});var o=function(){return o=Object.assign||function(t){for(var e,n=1,o=arguments.length;n<o;n++)for(var r in e=arguments[n])Object.prototype.hasOwnProperty.call(e,r)&&(t[r]=e[r]);return t},o.apply(this,arguments)};function r(t,e,n){void 0===e&&(e=Date.now()),void 0===n&&(n={});var r=o(o({},i),n||{}),s=(+t-+e)/1e3;if(Math.abs(s)<r.second)return{value:Math.round(s),unit:"second"};var a=s/60;if(Math.abs(a)<r.minute)return{value:Math.round(a),unit:"minute"};var c=s/3600;if(Math.abs(c)<r.hour)return{value:Math.round(c),unit:"hour"};var u=s/86400;if(Math.abs(u)<r.day)return{value:Math.round(u),unit:"day"};var h=new Date(t),l=new Date(e),d=h.getFullYear()-l.getFullYear();if(Math.round(Math.abs(d))>0)return{value:Math.round(d),unit:"year"};var p=12*d+h.getMonth()-l.getMonth();if(Math.round(Math.abs(p))>0)return{value:Math.round(p),unit:"month"};var v=s/604800;return{value:Math.round(v),unit:"week"}}var i={second:45,minute:45,hour:22,day:5}},14114:(t,e,n)=>{n.d(e,{P:()=>o});const o=t=>(e,n)=>{if(e.constructor._observers){if(!e.constructor.hasOwnProperty("_observers")){const t=e.constructor._observers;e.constructor._observers=new Map,t.forEach(((t,n)=>e.constructor._observers.set(n,t)))}}else{e.constructor._observers=new Map;const t=e.updated;e.updated=function(e){t.call(this,e),e.forEach(((t,e)=>{const n=this.constructor._observers.get(e);void 0!==n&&n.call(this,this[e],t)}))}}e.constructor._observers.set(n,t)}},63207:(t,e,n)=>{n(65660),n(15112);var o=n(9672),r=n(87156),i=n(50856),s=n(65233);(0,o.k)({_template:i.d`
    <style>
      :host {
        @apply --layout-inline;
        @apply --layout-center-center;
        position: relative;

        vertical-align: middle;

        fill: var(--iron-icon-fill-color, currentcolor);
        stroke: var(--iron-icon-stroke-color, none);

        width: var(--iron-icon-width, 24px);
        height: var(--iron-icon-height, 24px);
        @apply --iron-icon;
      }

      :host([hidden]) {
        display: none;
      }
    </style>
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:s.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(t){var e=(t||"").split(":");this._iconName=e.pop(),this._iconsetName=e.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(t){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,r.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,r.vz)(this.root).appendChild(this._img))}})},49075:(t,e,n)=>{n.d(e,{S:()=>s,B:()=>a});n(65233);var o=n(51644),r=n(26110),i=n(84938);const s={observers:["_focusedChanged(receivedFocusFromKeyboard)"],_focusedChanged:function(t){t&&this.ensureRipple(),this.hasRipple()&&(this._ripple.holdDown=t)},_createRipple:function(){var t=i.o._createRipple();return t.id="ink",t.setAttribute("center",""),t.classList.add("circle"),t}},a=[o.P,r.a,i.o,s]},25782:(t,e,n)=>{n(65233),n(65660),n(70019),n(97968);var o=n(9672),r=n(50856),i=n(33760);(0,o.k)({_template:r.d`
    <style include="paper-item-shared-styles"></style>
    <style>
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
        @apply --paper-icon-item;
      }

      .content-icon {
        @apply --layout-horizontal;
        @apply --layout-center;

        width: var(--paper-item-icon-width, 56px);
        @apply --paper-item-icon;
      }
    </style>

    <div id="contentIcon" class="content-icon">
      <slot name="item-icon"></slot>
    </div>
    <slot></slot>
`,is:"paper-icon-item",behaviors:[i.U]})},21560:(t,e,n)=>{n.d(e,{ZH:()=>h,MT:()=>i,U2:()=>c,RV:()=>r,t8:()=>u});const o=function(){if(!(!navigator.userAgentData&&/Safari\//.test(navigator.userAgent)&&!/Chrom(e|ium)\//.test(navigator.userAgent))||!indexedDB.databases)return Promise.resolve();let t;return new Promise((e=>{const n=()=>indexedDB.databases().finally(e);t=setInterval(n,100),n()})).finally((()=>clearInterval(t)))};function r(t){return new Promise(((e,n)=>{t.oncomplete=t.onsuccess=()=>e(t.result),t.onabort=t.onerror=()=>n(t.error)}))}function i(t,e){const n=o().then((()=>{const n=indexedDB.open(t);return n.onupgradeneeded=()=>n.result.createObjectStore(e),r(n)}));return(t,o)=>n.then((n=>o(n.transaction(e,t).objectStore(e))))}let s;function a(){return s||(s=i("keyval-store","keyval")),s}function c(t,e=a()){return e("readonly",(e=>r(e.get(t))))}function u(t,e,n=a()){return n("readwrite",(n=>(n.put(e,t),r(n.transaction))))}function h(t=a()){return t("readwrite",(t=>(t.clear(),r(t.transaction))))}},32930:(t,e,n)=>{n.d(e,{v:()=>r});var o=n(39030);function r(t="",e=!1,n=""){return(0,o.eZ)({descriptor:o=>({get(){var o,r,i;const s="slot"+(t?`[name=${t}]`:":not([name])");let a=null!==(i=null===(r=null===(o=this.renderRoot)||void 0===o?void 0:o.querySelector(s))||void 0===r?void 0:r.assignedNodes({flatten:e}))&&void 0!==i?i:[];return n&&(a=a.filter((t=>t.nodeType===Node.ELEMENT_NODE&&t.matches(n)))),a},enumerable:!0,configurable:!0})})}}}]);
//# sourceMappingURL=076cc30c.js.map