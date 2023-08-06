"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[13997],{81545:(e,t,i)=>{i(93883);var r=i(37500),o=i(26767),n=i(5701),a=i(67352);function s(){s=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var o=t.placement;if(t.kind===r&&("static"===o||"prototype"===o)){var n="static"===o?e:i;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!d(e))return i.push(e);var t=this.decorateElement(e,o);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var n=this.decorateConstructor(i,t);return r.push.apply(r,n.finishers),n.finishers=r,n},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],o=e.decorators,n=o.length-1;n>=0;n--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[n])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);i.push.apply(i,c)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[r])(o)||o);if(void 0!==n.finisher&&i.push(n.finisher),void 0!==n.elements){e=n.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return u(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?u(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=m(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:i,placement:r,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:p(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=p(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function l(e){var t,i=m(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function c(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function d(e){return e.decorators&&e.decorators.length}function h(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function p(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function m(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function u(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}!function(e,t,i,r){var o=s();if(r)for(var n=0;n<r.length;n++)o=r[n](o);var a=t((function(e){o.initializeInstanceElements(e,p.elements)}),i),p=o.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},r=0;r<e.length;r++){var o,n=e[r];if("method"===n.kind&&(o=t.find(i)))if(h(n.descriptor)||h(o.descriptor)){if(d(n)||d(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(d(n)){if(d(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}c(n,o)}else t.push(n)}return t}(a.d.map(l)),e);o.initializeClassElements(a.F,p.elements),o.runClassFinishers(a.F,p.finishers)}([(0,o.M)("ha-button-menu")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.C)()],key:"corner",value:()=>"TOP_START"},{kind:"field",decorators:[(0,n.C)({type:Boolean})],key:"multi",value:()=>!1},{kind:"field",decorators:[(0,n.C)({type:Boolean})],key:"activatable",value:()=>!1},{kind:"field",decorators:[(0,n.C)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,n.C)({type:Boolean})],key:"fixed",value:()=>!1},{kind:"field",decorators:[(0,a.I)("mwc-menu",!0)],key:"_menu",value:void 0},{kind:"get",key:"items",value:function(){var e;return null===(e=this._menu)||void 0===e?void 0:e.items}},{kind:"get",key:"selected",value:function(){var e;return null===(e=this._menu)||void 0===e?void 0:e.selected}},{kind:"method",key:"render",value:function(){return r.dy`
      <div @click=${this._handleClick}>
        <slot name="trigger"></slot>
      </div>
      <mwc-menu
        .corner=${this.corner}
        .fixed=${this.fixed}
        .multi=${this.multi}
        .activatable=${this.activatable}
      >
        <slot></slot>
      </mwc-menu>
    `}},{kind:"method",key:"_handleClick",value:function(){this.disabled||(this._menu.anchor=this,this._menu.show())}},{kind:"get",static:!0,key:"styles",value:function(){return r.iv`
      :host {
        display: inline-block;
        position: relative;
      }
      ::slotted([disabled]) {
        color: var(--disabled-text-color);
      }
    `}}]}}),r.oi)},36125:(e,t,i)=>{var r=i(95916);function o(){o=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var o=t.placement;if(t.kind===r&&("static"===o||"prototype"===o)){var n="static"===o?e:i;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!s(e))return i.push(e);var t=this.decorateElement(e,o);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var n=this.decorateConstructor(i,t);return r.push.apply(r,n.finishers),n.finishers=r,n},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],o=e.decorators,n=o.length-1;n>=0;n--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[n])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);i.push.apply(i,c)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[r])(o)||o);if(void 0!==n.finisher&&i.push(n.finisher),void 0!==n.elements){e=n.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return h(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?h(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=d(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:i,placement:r,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:c(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=c(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function n(e){var t,i=d(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function a(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function s(e){return e.decorators&&e.decorators.length}function l(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function c(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function d(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function h(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function p(e,t,i){return p="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=m(e)););return e}(e,t);if(r){var o=Object.getOwnPropertyDescriptor(r,t);return o.get?o.get.call(i):o.value}},p(e,t,i||e)}function m(e){return m=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},m(e)}!function(e,t,i,r){var c=o();if(r)for(var d=0;d<r.length;d++)c=r[d](c);var h=t((function(e){c.initializeInstanceElements(e,p.elements)}),i),p=c.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},r=0;r<e.length;r++){var o,n=e[r];if("method"===n.kind&&(o=t.find(i)))if(l(n.descriptor)||l(o.descriptor)){if(s(n)||s(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(s(n)){if(s(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}a(n,o)}else t.push(n)}return t}(h.d.map(n)),e);c.initializeClassElements(h.F,p.elements),c.runClassFinishers(h.F,p.finishers)}([(0,i(26767).M)("ha-fab")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"method",key:"firstUpdated",value:function(e){p(m(i.prototype),"firstUpdated",this).call(this,e),this.style.setProperty("--mdc-theme-secondary","var(--primary-color)")}}]}}),r.L)},13997:(e,t,i)=>{i(53918),i(87502),i(44577),i(53973),i(51095),i(54444);var r=i(37500),o=i(26767),n=i(5701),a=i(17717),s=i(67352),l=i(84982),c=i(228),d=i(48399),h=i(47501),p=i(47181),m=i(87744),u=i(38346),f=i(69371),y=i(26765),v=i(54845),g=i(11654),b=i(27322);i(74535),i(81545),i(22098),i(31206),i(36125),i(10983),i(52039);const w=()=>Promise.all([i.e(45243),i.e(54619),i.e(25230),i.e(18607),i.e(91453),i.e(88454),i.e(72753),i.e(27207),i.e(37797)]).then(i.bind(i,24841));function k(){k=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var o=t.placement;if(t.kind===r&&("static"===o||"prototype"===o)){var n="static"===o?e:i;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!E(e))return i.push(e);var t=this.decorateElement(e,o);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var n=this.decorateConstructor(i,t);return r.push.apply(r,n.finishers),n.finishers=r,n},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],o=e.decorators,n=o.length-1;n>=0;n--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[n])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);i.push.apply(i,c)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[r])(o)||o);if(void 0!==n.finisher&&i.push(n.finisher),void 0!==n.elements){e=n.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return z(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?z(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=C(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:i,placement:r,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:P(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=P(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function _(e){var t,i=C(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function x(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function E(e){return e.decorators&&e.decorators.length}function $(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function P(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function C(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function z(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function A(e,t,i){return A="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=D(e)););return e}(e,t);if(r){var o=Object.getOwnPropertyDescriptor(r,t);return o.get?o.get.call(i):o.value}},A(e,t,i||e)}function D(e){return D=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},D(e)}const I="M8,5.14V19.14L19,12.14L8,5.14Z",T="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",O="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z";!function(e,t,i,r){var o=k();if(r)for(var n=0;n<r.length;n++)o=r[n](o);var a=t((function(e){o.initializeInstanceElements(e,s.elements)}),i),s=o.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},r=0;r<e.length;r++){var o,n=e[r];if("method"===n.kind&&(o=t.find(i)))if($(n.descriptor)||$(o.descriptor)){if(E(n)||E(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(E(n)){if(E(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}x(n,o)}else t.push(n)}return t}(a.d.map(_)),e);o.initializeClassElements(a.F,s.elements),o.runClassFinishers(a.F,s.finishers)}([(0,o.M)("ha-media-player-browse")],(function(e,t){class o extends t{constructor(...t){super(...t),e(this)}}return{F:o,d:[{kind:"field",decorators:[(0,n.C)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.C)()],key:"entityId",value:void 0},{kind:"field",decorators:[(0,n.C)()],key:"mediaContentId",value:void 0},{kind:"field",decorators:[(0,n.C)()],key:"mediaContentType",value:void 0},{kind:"field",decorators:[(0,n.C)()],key:"action",value:()=>"play"},{kind:"field",decorators:[(0,n.C)({type:Boolean})],key:"dialog",value:()=>!1},{kind:"field",decorators:[(0,n.C)({type:Boolean,attribute:"narrow",reflect:!0})],key:"_narrow",value:()=>!1},{kind:"field",decorators:[(0,n.C)({type:Boolean,attribute:"scroll",reflect:!0})],key:"_scrolled",value:()=>!1},{kind:"field",decorators:[(0,a.S)()],key:"_loading",value:()=>!1},{kind:"field",decorators:[(0,a.S)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,a.S)()],key:"_mediaPlayerItems",value:()=>[]},{kind:"field",decorators:[(0,s.I)(".header")],key:"_header",value:void 0},{kind:"field",decorators:[(0,s.I)(".content")],key:"_content",value:void 0},{kind:"field",key:"_headerOffsetHeight",value:()=>0},{kind:"field",key:"_resizeObserver",value:void 0},{kind:"method",key:"connectedCallback",value:function(){A(D(o.prototype),"connectedCallback",this).call(this),this.updateComplete.then((()=>this._attachObserver()))}},{kind:"method",key:"disconnectedCallback",value:function(){this._resizeObserver&&this._resizeObserver.disconnect()}},{kind:"method",key:"navigateBack",value:function(){this._mediaPlayerItems.pop();const e=this._mediaPlayerItems.pop();e&&this._navigate(e)}},{kind:"method",key:"render",value:function(){var e;if(this._loading)return r.dy`<ha-circular-progress active></ha-circular-progress>`;if(this._error&&!this._mediaPlayerItems.length){if(!this.dialog)return r.dy`
          <div class="container">${this._renderError(this._error)}</div>
        `;this._closeDialogAction(),(0,y.Ys)(this,{title:this.hass.localize("ui.components.media-browser.media_browsing_error"),text:this._renderError(this._error)})}if(!this._mediaPlayerItems.length)return r.dy``;const t=this._mediaPlayerItems[this._mediaPlayerItems.length-1],i="media-source://media_source/galeria/."===t.media_content_id,o=this._mediaPlayerItems.length>1?this._mediaPlayerItems[this._mediaPlayerItems.length-2]:void 0,n=this.hass.localize(`ui.components.media-browser.class.${t.media_class}`),a=f.Fn[t.media_class],s=f.Fn[t.children_media_class];return r.dy`
      <div
        class="header ${(0,c.$)({"no-img":!t.thumbnail,"no-dialog":!this.dialog})}"
        @transitionend=${this._setHeaderHeight}
      >
        <div class="header-content">
          ${t.thumbnail?r.dy`
                <div
                  class="img"
                  style=${(0,h.V)({backgroundImage:t.thumbnail?`url(${t.thumbnail})`:"none"})}
                >
                  ${this._narrow&&null!=t&&t.can_play?r.dy`
                        <ha-fab
                          mini
                          .item=${t}
                          @click=${this._actionClicked}
                        >
                          <ha-svg-icon
                            slot="icon"
                            .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                            .path=${"play"===this.action?I:T}
                          ></ha-svg-icon>
                          ${this.hass.localize(`ui.components.media-browser.${this.action}`)}
                        </ha-fab>
                      `:""}
                </div>
              `:r.dy``}
          <div class="header-info">
            <div class="breadcrumb">
              ${o?r.dy`
                    <div class="previous-title" @click=${this.navigateBack}>
                      <ha-svg-icon .path=${"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}></ha-svg-icon>
                      ${o.title}
                    </div>
                  `:""}
              <h1 class="title">${t.title}</h1>
              ${n?r.dy` <h2 class="subtitle">${n}</h2> `:""}
            </div>
            ${!t.can_play||t.thumbnail&&this._narrow?"":r.dy`
                  <mwc-button
                    raised
                    .item=${t}
                    @click=${this._actionClicked}
                  >
                    <ha-svg-icon
                      .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                      .path=${"play"===this.action?I:T}
                    ></ha-svg-icon>
                    ${this.hass.localize(`ui.components.media-browser.${this.action}`)}
                  </mwc-button>
                `}
          </div>
        </div>
        ${this.dialog?r.dy`
              <ha-icon-button
                .label=${this.hass.localize("ui.dialogs.generic.close")}
                .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                @click=${this._closeDialogAction}
                class="header_button"
                dir=${(0,m.Zu)(this.hass)}
              ></ha-icon-button>
            `:""}
      </div>
      <div class="content" @scroll=${this._scroll} @touchmove=${this._scroll}>
        ${this._error?r.dy`
              <div class="container">${this._renderError(this._error)}</div>
            `:null!==(e=t.children)&&void 0!==e&&e.length?"grid"===s.layout?r.dy`
                <div
                  class="children ${(0,c.$)({portrait:"portrait"===s.thumbnail_ratio})}"
                >
                  ${t.children.map((e=>r.dy`
                      <div
                        class="child"
                        .item=${e}
                        @click=${this._childClicked}
                      >
                        <div class="ha-card-parent">
                          <ha-card
                            outlined
                            style=${(0,h.V)({backgroundImage:e.thumbnail?`url(${e.thumbnail})`:"none"})}
                          >
                            ${e.thumbnail?"":r.dy`
                                  <ha-svg-icon
                                    class="folder"
                                    .path=${f.Fn["directory"===e.media_class&&e.children_media_class||e.media_class].icon}
                                  ></ha-svg-icon>
                                `}
                          </ha-card>
                          ${e.can_play?r.dy`
                                <ha-icon-button
                                  class="play ${(0,c.$)({can_expand:e.can_expand})}"
                                  .item=${e}
                                  .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                                  .path=${"play"===this.action?I:T}
                                  @click=${this._actionClicked}
                                ></ha-icon-button>
                              `:""}
                        </div>
                        <!-- AIS add info button for admins only aisGallery-->
                        ${this._getAisImageButtons(i,e,s.layout||"")}
                      </div>
                    `))}
                </div>
              `:r.dy`
                <mwc-list>
                  ${t.children.map((e=>r.dy`
                      <mwc-list-item
                        @click=${this._childClicked}
                        .item=${e}
                        graphic="avatar"
                        hasMeta
                        dir=${(0,m.Zu)(this.hass)}
                      >
                        <div
                          class="graphic"
                          style=${(0,d.o)(a.show_list_images&&e.thumbnail?`background-image: url(${e.thumbnail})`:void 0)}
                          slot="graphic"
                        >
                          <ha-icon-button
                            class="play ${(0,c.$)({show:!a.show_list_images||!e.thumbnail})}"
                            .item=${e}
                            .label=${this.hass.localize(`ui.components.media-browser.${this.action}-media`)}
                            .path=${"play"===this.action?I:T}
                            @click=${this._actionClicked}
                          ></ha-icon-button>
                        </div>
                        <span class="title">${e.title}</span>
                        <!-- AIS add info button for admins only aisGallery-->
                        ${this._getAisImageButtons(i,e,s.layout||"")}
                      </mwc-list-item>
                      <li divider role="separator"></li>
                    `))}
                </mwc-list>
              `:r.dy`
              <div class="container">
                ${this.hass.localize("ui.components.media-browser.no_items")}
                <br />
                ${i?r.dy`<br />${this.hass.localize("ui.components.media-browser.learn_adding_local_media","documentation",r.dy`<a
                          href="https://www.ai-speaker.com/docs/ais_app_integration_gallery"
                          target="_blank"
                          rel="noreferrer"
                          >${this.hass.localize("ui.components.media-browser.documentation")}</a
                        >`)}
                      <br />
                      ${this.hass.localize("ui.components.media-browser.local_media_files")}`:""}
              </div>
            `}
        ${this._getAisImageFabButton(i)}
      </div>
    `}},{kind:"method",key:"firstUpdated",value:function(){this._measureCard(),this._attachObserver()}},{kind:"method",key:"updated",value:function(e){A(D(o.prototype),"updated",this).call(this,e),e.has("_mediaPlayerItems")&&this._mediaPlayerItems.length&&this._setHeaderHeight(),void 0!==e.get("_scrolled")&&this._mediaPlayerItems.length&&this._animateHeaderHeight(),(e.has("entityId")||e.has("mediaContentId")||e.has("mediaContentType")||e.has("action"))&&(e.has("entityId")&&(this._error=void 0,this._mediaPlayerItems=[]),this._fetchData(this.mediaContentId,this.mediaContentType).then((e=>{e&&(this._mediaPlayerItems=[e])})).catch((e=>{this._error=e})))}},{kind:"method",key:"_setHeaderHeight",value:async function(){await this.updateComplete;const e=this._header,t=this._content;e&&t&&(this._headerOffsetHeight=e.offsetHeight,t.style.marginTop=`${this._headerOffsetHeight}px`,t.style.maxHeight=`calc(var(--media-browser-max-height, 100%) - ${this._headerOffsetHeight}px)`)}},{kind:"method",key:"_animateHeaderHeight",value:function(){let e;const t=i=>{void 0===e&&(e=i);const r=i-e;this._setHeaderHeight(),r<400&&requestAnimationFrame(t)};requestAnimationFrame(t)}},{kind:"method",key:"_actionClicked",value:function(e){e.stopPropagation();const t=e.currentTarget.item;this._runAction(t)}},{kind:"method",key:"_getAisImageFabButton",value:function(e){return e?r.dy` <mwc-fab
        slot="fab"
        title="Dodaj"
        @click=${this._addImage}
        class="addImageFab"
      >
        <ha-svg-icon slot="icon" path=${T}></ha-svg-icon>
      </mwc-fab>`:r.dy``}},{kind:"method",key:"_getAisImageButtons",value:function(e,t,i){const o="grid"===i?"":"Line";return this.hass.user.is_admin&&e?r.dy` <div class="aisButtons${o}">
        <mwc-icon-button
          class="aisButton${o} aisInfoButton"
          .item=${t}
          @click=${this._actionClickedInfo}
        >
          <ha-svg-icon path=${O}></ha-svg-icon>
        </mwc-icon-button>
        <mwc-icon-button
          class="aisButton${o} aisEditButton"
          .item=${t}
          @click=${this._actionClickedEdit}
        >
          <ha-svg-icon path=${"M22.7 14.3L21.7 15.3L19.7 13.3L20.7 12.3C20.8 12.2 20.9 12.1 21.1 12.1C21.2 12.1 21.4 12.2 21.5 12.3L22.8 13.6C22.9 13.8 22.9 14.1 22.7 14.3M13 19.9V22H15.1L21.2 15.9L19.2 13.9L13 19.9M21 5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H11V19.1L12.1 18H5L8.5 13.5L11 16.5L14.5 12L16.1 14.1L21 9.1V5Z"}></ha-svg-icon>
        </mwc-icon-button>
        <mwc-icon-button
          class="aisButton${o} aisDeleteButton"
          .item=${t}
          @click=${this._actionClickedDelete}
        >
          <ha-svg-icon path=${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}></ha-svg-icon>
        </mwc-icon-button>
      </div>`:t.can_play&&this.hass.user.is_admin&&!e?r.dy` <div class="aisButtons${o}">
        <mwc-icon-button
          class="aisButton${o} aisInfoButton"
          .item=${t}
          @click=${this._actionClickedInfo}
        >
          <ha-svg-icon path=${O}></ha-svg-icon>
        </mwc-icon-button>
      </div>`:e?r.dy``:r.dy` <div class="title">
          ${t.title}
          <paper-tooltip fitToVisibleBounds position="top" offset="4"
            >${t.title}</paper-tooltip
          >
        </div>
        <div class="type">
          ${this.hass.localize(`ui.components.media-browser.content-type.${t.media_content_type}`)}
        </div>`}},{kind:"method",key:"_actionClickedInfo",value:async function(e){e.stopPropagation();const t=e.currentTarget.item,r=await this.hass.callWS({type:"media_source/resolve_media",media_content_id:t.media_content_id});var o,n;o=this,n={sourceUrl:r.url,sourceType:r.mime_type,sourceThumbnail:t.thumbnail,title:t.title},(0,p.B)(o,"show-dialog",{dialogTag:"hui-dialog-web-browser-ais-play-media",dialogImport:()=>Promise.all([i.e(45243),i.e(25230),i.e(91453),i.e(319),i.e(72753),i.e(89239)]).then(i.bind(i,112)),dialogParams:n})}},{kind:"method",key:"_actionClickedEdit",value:async function(e){e.stopPropagation();const t=e.currentTarget.item,r=await this.hass.callWS({type:"media_source/resolve_media",media_content_id:t.media_content_id});(0,p.B)(this,"show-dialog",{dialogTag:"hui-dialog-web-browser-ais-edit-image",dialogImport:()=>Promise.all([i.e(75009),i.e(42955),i.e(45243),i.e(54619),i.e(25230),i.e(18607),i.e(91453),i.e(28659),i.e(319),i.e(72753),i.e(56668)]).then(i.bind(i,85494)),dialogParams:{sourceUrl:r.url,sourceType:r.mime_type,title:t.title}})}},{kind:"method",key:"_actionClickedDelete",value:async function(e){e.stopPropagation();const t=e.currentTarget.item;if(await(0,y.g7)(this,{title:t.title,text:"Jesteś pewny, że chcesz usunąć ten plik?",confirmText:"TAK",dismissText:"NIE"})){const e=await this.hass.callWS({type:"media_source/resolve_media",media_content_id:t.media_content_id});await this.hass.callService("ais_files","remove_file",{path:e.url}),this._navigate(this._mediaPlayerItems[this._mediaPlayerItems.length-1])}}},{kind:"method",key:"_runAction",value:function(e){(0,p.B)(this,"media-picked",{item:e})}},{kind:"method",key:"_childClicked",value:async function(e){const t=e.currentTarget.item;t&&(t.can_expand?this._navigate(t):this._runAction(t))}},{kind:"method",key:"_navigate",value:async function(e){var t;let i;this._error=void 0;try{i=await this._fetchData(e.media_content_id,e.media_content_type)}catch(e){return(0,y.Ys)(this,{title:this.hass.localize("ui.components.media-browser.media_browsing_error"),text:this._renderError(e)}),void(this._loading=!1)}null===(t=this._content)||void 0===t||t.scrollTo(0,0),this._scrolled=!1,this._mediaPlayerItems=[...this._mediaPlayerItems,i]}},{kind:"method",key:"_fetchData",value:async function(e,t){let i;this._loading=!0;try{i=this.entityId!==f.N8?await(0,f.zz)(this.hass,this.entityId,e,t):await(0,f.b)(this.hass,e,t)}finally{this._loading=!1}return i}},{kind:"method",key:"_measureCard",value:function(){this._narrow=(this.dialog?window.innerWidth:this.offsetWidth)<450}},{kind:"method",decorators:[(0,l.h)({passive:!0})],key:"_scroll",value:function(e){const t=e.currentTarget;!this._scrolled&&t.scrollTop>this._headerOffsetHeight?this._scrolled=!0:this._scrolled&&t.scrollTop<this._headerOffsetHeight&&(this._scrolled=!1)}},{kind:"method",key:"_attachObserver",value:async function(){this._resizeObserver||(await(0,v.P)(),this._resizeObserver=new ResizeObserver((0,u.D)((()=>this._measureCard()),250,!1))),this._resizeObserver.observe(this)}},{kind:"method",key:"_closeDialogAction",value:function(){(0,p.B)(this,"close-dialog")}},{kind:"method",key:"_renderError",value:function(e){return"Media directory does not exist."===e.message?r.dy`
        <h2>
          ${this.hass.localize("ui.components.media-browser.no_local_media_found")}
        </h2>
        <p>
          ${this.hass.localize("ui.components.media-browser.no_media_folder")}
          <br />
          ${this.hass.localize("ui.components.media-browser.setup_local_help","documentation",r.dy`<a
              href=${(0,b.R)(this.hass,"/more-info/local-media/setup-media")}
              target="_blank"
              rel="noreferrer"
              >${this.hass.localize("ui.components.media-browser.documentation")}</a
            >`)}
          <br />
          ${this.hass.localize("ui.components.media-browser.local_media_files")}
        </p>
      `:r.dy`<span class="error">${e.message}</span>`}},{kind:"method",key:"_addImage",value:function(){const e=this._mediaPlayerItems[this._mediaPlayerItems.length-1];((e,t)=>{(0,p.B)(e,"show-dialog",{dialogTag:"ha-dialog-aisgalery",dialogImport:w,dialogParams:t})})(this,{jsCallback:()=>{this._navigate(e)}})}},{kind:"get",static:!0,key:"styles",value:function(){return[g.Qx,r.iv`
        :host {
          display: flex;
          flex-direction: column;
          position: relative;
        }

        ha-circular-progress {
          --mdc-theme-primary: var(--primary-color);
          display: flex;
          justify-content: center;
          margin: 40px;
        }

        .container {
          padding: 16px;
        }

        .content {
          overflow-y: auto;
          padding-bottom: 20px;
          box-sizing: border-box;
        }

        .header {
          display: flex;
          justify-content: space-between;
          border-bottom: 1px solid var(--divider-color);
          background-color: var(--card-background-color);
          position: absolute;
          top: 0;
          right: 0;
          left: 0;
          z-index: 5;
          padding: 20px 24px 10px;
        }

        .header_button {
          position: relative;
          right: -8px;
        }

        .header-content {
          display: flex;
          flex-wrap: wrap;
          flex-grow: 1;
          align-items: flex-start;
        }

        .header-content .img {
          height: 200px;
          width: 200px;
          margin-right: 16px;
          background-size: cover;
          border-radius: 4px;
          transition: width 0.4s, height 0.4s;
        }

        .header-info {
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-self: stretch;
          min-width: 0;
          flex: 1;
        }

        .header-info mwc-button {
          display: block;
          --mdc-theme-primary: var(--primary-color);
        }

        .breadcrumb {
          display: flex;
          flex-direction: column;
          overflow: hidden;
          flex-grow: 1;
        }

        .breadcrumb .title {
          font-size: 32px;
          line-height: 1.2;
          font-weight: bold;
          margin: 0;
          overflow: hidden;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          padding-right: 8px;
        }

        .breadcrumb .previous-title {
          font-size: 14px;
          padding-bottom: 8px;
          color: var(--secondary-text-color);
          overflow: hidden;
          text-overflow: ellipsis;
          cursor: pointer;
          --mdc-icon-size: 14px;
        }

        .breadcrumb .subtitle {
          font-size: 16px;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-bottom: 0;
          transition: height 0.5s, margin 0.5s;
        }

        /* ============= CHILDREN ============= */

        mwc-list {
          --mdc-list-vertical-padding: 0;
          --mdc-list-item-graphic-margin: 0;
          --mdc-theme-text-icon-on-background: var(--secondary-text-color);
          margin-top: 10px;
        }

        mwc-list li:last-child {
          display: none;
        }

        mwc-list li[divider] {
          border-bottom-color: var(--divider-color);
        }

        .children {
          display: grid;
          grid-template-columns: repeat(
            auto-fit,
            minmax(var(--media-browse-item-size, 175px), 0.1fr)
          );
          grid-gap: 16px;
          padding: 0px 24px;
          margin: 8px 0px;
        }

        :host([dialog]) .children {
          grid-template-columns: repeat(
            auto-fit,
            minmax(var(--media-browse-item-size, 175px), 0.33fr)
          );
        }

        .child {
          display: flex;
          flex-direction: column;
          cursor: pointer;
        }

        .ha-card-parent {
          position: relative;
          width: 100%;
        }

        .children ha-card {
          width: 100%;
          padding-bottom: 100%;
          position: relative;
          box-sizing: border-box;
          background-size: cover;
          background-repeat: no-repeat;
          background-position: center;
          transition: padding-bottom 0.1s ease-out;
        }

        .portrait.children ha-card {
          padding-bottom: 150%;
        }

        .child .folder,
        .child .play {
          position: absolute;
        }

        .child .folder {
          color: var(--secondary-text-color);
          top: calc(50% - (var(--mdc-icon-size) / 2));
          left: calc(50% - (var(--mdc-icon-size) / 2));
          --mdc-icon-size: calc(var(--media-browse-item-size, 175px) * 0.4);
        }

        .child .play {
          transition: color 0.5s;
          border-radius: 50%;
          bottom: calc(50% - 35px);
          right: calc(50% - 35px);
          opacity: 0;
          transition: opacity 0.1s ease-out;
        }

        .child .play:not(.can_expand) {
          --mdc-icon-button-size: 70px;
          --mdc-icon-size: 48px;
        }

        .ha-card-parent:hover .play:not(.can_expand) {
          opacity: 1;
          color: var(--primary-color);
        }

        .child .play.can_expand {
          opacity: 1;
          bottom: -4px;
          right: 4px;
          z-index: 9999;
        }

        .child .play:hover {
          color: var(--primary-color);
        }

        .ha-card-parent:hover ha-card {
          opacity: 0.5;
        }

        .child .title {
          font-size: 16px;
          padding-top: 8px;
          padding-left: 2px;
          overflow: hidden;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          text-overflow: ellipsis;
        }

        .child .type {
          font-size: 12px;
          color: var(--secondary-text-color);
          padding-left: 2px;
        }

        mwc-list-item .graphic {
          background-size: cover;
        }

        mwc-list-item .graphic .play {
          opacity: 0;
          transition: all 0.5s;
          background-color: rgba(var(--rgb-card-background-color), 0.5);
          border-radius: 50%;
          --mdc-icon-button-size: 40px;
        }

        mwc-list-item:hover .graphic .play {
          opacity: 1;
          color: var(--primary-color);
        }

        mwc-list-item .graphic .play.show {
          opacity: 1;
          background-color: transparent;
        }

        mwc-list-item .title {
          margin-left: 16px;
        }
        mwc-list-item[dir="rtl"] .title {
          margin-right: 16px;
          margin-left: 0;
        }

        /* ============= Narrow ============= */

        :host([narrow]) {
          padding: 0;
        }

        :host([narrow]) .breadcrumb .title {
          font-size: 24px;
        }

        :host([narrow]) .header {
          padding: 0;
        }

        :host([narrow]) .header.no-dialog {
          display: block;
        }

        :host([narrow]) .header_button {
          position: absolute;
          top: 14px;
          right: 8px;
        }

        :host([narrow]) .header-content {
          flex-direction: column;
          flex-wrap: nowrap;
        }

        :host([narrow]) .header-content .img {
          height: auto;
          width: 100%;
          margin-right: 0;
          padding-bottom: 50%;
          margin-bottom: 8px;
          position: relative;
          background-position: center;
          border-radius: 0;
          transition: width 0.4s, height 0.4s, padding-bottom 0.4s;
        }

        ha-fab {
          position: absolute;
          --mdc-theme-secondary: var(--primary-color);
          bottom: -20px;
          right: 20px;
        }

        :host([narrow]) .header-info mwc-button {
          margin-top: 16px;
          margin-bottom: 8px;
        }

        :host([narrow]) .header-info {
          padding: 20px 24px 10px;
        }

        :host([narrow]) .media-source {
          padding: 0 24px;
        }

        :host([narrow]) .children {
          grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
        }

        /* ============= Scroll ============= */

        :host([scroll]) .breadcrumb .subtitle {
          height: 0;
          margin: 0;
        }

        :host([scroll]) .breadcrumb .title {
          -webkit-line-clamp: 1;
        }

        :host(:not([narrow])[scroll]) .header:not(.no-img) ha-icon-button {
          align-self: center;
        }

        :host([scroll]) .header-info mwc-button,
        .no-img .header-info mwc-button {
          padding-right: 4px;
        }

        :host([scroll][narrow]) .no-img .header-info mwc-button {
          padding-right: 16px;
        }

        :host([scroll]) .header-info {
          flex-direction: row;
        }

        :host([scroll]) .header-info mwc-button {
          align-self: center;
          margin-top: 0;
          margin-bottom: 0;
        }

        :host([scroll][narrow]) .no-img .header-info {
          flex-direction: row-reverse;
        }

        :host([scroll][narrow]) .header-info {
          padding: 20px 24px 10px 24px;
          align-items: center;
        }

        :host([scroll]) .header-content {
          align-items: flex-end;
          flex-direction: row;
        }

        :host([scroll]) .header-content .img {
          height: 75px;
          width: 75px;
        }

        :host([scroll][narrow]) .header-content .img {
          height: 100px;
          width: 100px;
          padding-bottom: initial;
          margin-bottom: 0;
        }

        :host([scroll]) ha-fab {
          bottom: 4px;
          right: 4px;
          --mdc-fab-box-shadow: none;
          --mdc-theme-secondary: rgba(var(--rgb-primary-color), 0.5);
        }
        /* AIS css start */
        mwc-list-item {
          display: block;
        }
        mwc-fab.addImageFab {
          position: fixed !important;
          bottom: 16px !important;
          right: 26px !important;
          --mdc-theme-secondary: var(--accent-color) !important;
        }
        mwc-icon-button.aisInfoButton {
          position: relative !important;
        }
        div.aisButtons {
          position: relative;
          width: 100%;
          height: 3em;
          display: flex;
          bottom: 3em;
          margin-bottom: -3em;
          background-color: #9e9e9e8a;
        }
        div.aisButtonsLine {
          float: right;
          position: relative;
        }
        mwc-icon-button.aisButton.aisDeleteButton {
          margin-left: auto;
        }
        mwc-icon-button.aisInfoButton:hover {
          color: var(--primary-color);
        }
        mwc-icon-button.aisEditButton:hover {
          color: var(--primary-color);
        }
        mwc-icon-button.aisDeleteButton:hover {
          color: var(--error-color);
        }
      `]}}]}}),r.oi)},27322:(e,t,i)=>{i.d(t,{R:()=>r});const r=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`}}]);
//# sourceMappingURL=59d8d9f6.js.map