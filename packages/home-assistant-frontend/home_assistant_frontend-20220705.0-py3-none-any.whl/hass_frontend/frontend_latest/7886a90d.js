"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[58040],{55070:(e,t,r)=>{r.d(t,{Eu:()=>n,hZ:()=>s});const i=["#44739e","#984ea3","#00d2d5","#ff7f00","#af8d00","#7f80cd","#b3e900","#c42e60","#a65628","#f781bf","#8dd3c7","#bebada","#fb8072","#80b1d3","#fdb462","#fccde5","#bc80bd","#ffed6f","#c4eaff","#cf8c00","#1b9e77","#d95f02","#e7298a","#e6ab02","#a6761d","#0097ff","#00d067","#f43600","#4ba93b","#5779bb","#927acc","#97ee3f","#bf3947","#9f5b00","#f48758","#8caed6","#f2b94f","#eff26e","#e43872","#d9b100","#9d7a00","#698cff","#d9d9d9","#00d27e","#d06800","#009f82","#c49200","#cbe8ff","#fecddf","#c27eb6","#8cd2ce","#c4b8d9","#f883b0","#a49100","#f48800","#27d0df","#a04a9b"];function n(e){return i[e%i.length]}function s(e,t){return t.getPropertyValue(`--graph-color-${e+1}`)||n(e)}},349:(e,t,r)=>{function i(e,t,r){return t in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}r.d(t,{m:()=>o});class n{constructor(e=!0){i(this,"_storage",{}),i(this,"_listeners",{}),e&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}addFromStorage(e){if(!this._storage[e]){const t=window.localStorage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const r=this._listeners[e].indexOf(t);-1!==r&&this._listeners[e].splice(r,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){this._storage[e]=t;try{window.localStorage.setItem(e,JSON.stringify(t))}catch(e){}}}const s=new n,o=(e,t,r=!0,i)=>o=>{const a=r?s:new n(!1),l=String(o.key);e=e||String(o.key);const c=o.initializer?o.initializer():void 0;a.addFromStorage(e);const d=()=>a.hasKey(e)?a.getValue(e):c;return{kind:"method",placement:"prototype",key:o.key,descriptor:{set(r){((r,i)=>{let n;t&&(n=d()),a.setValue(e,i),t&&r.requestUpdate(o.key,n)})(this,r)},get:()=>d(),enumerable:!0,configurable:!0},finisher(n){if(t&&r){const t=n.prototype.connectedCallback,r=n.prototype.disconnectedCallback;n.prototype.connectedCallback=function(){var r;t.call(this),this[`__unbsubLocalStorage${l}`]=(r=this,a.subscribeChanges(e,(e=>{r.requestUpdate(o.key,e)})))},n.prototype.disconnectedCallback=function(){r.call(this),this[`__unbsubLocalStorage${l}`]()}}t&&n.createProperty(o.key,{noAccessor:!0,...i})}}}},16235:(e,t,r)=>{var i=r(37500);function n(){n=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var s="static"===n?e:r;this.defineClassElement(s,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!a(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var s=this.decorateConstructor(r,t);return i.push.apply(i,s.finishers),s.finishers=i,s},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,s=n.length-1;s>=0;s--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[s])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),s=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==s.finisher&&r.push(s.finisher),void 0!==s.elements){e=s.elements;for(var o=0;o<e.length-1;o++)for(var a=o+1;a<e.length;a++)if(e[o].key===e[a].key&&e[o].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return h(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?h(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=d(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var s={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),s.initializer=e.initializer),s},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:c(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=c(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function s(e){var t,r=d(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function o(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function a(e){return e.decorators&&e.decorators.length}function l(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function c(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function d(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function h(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var c=n();if(i)for(var d=0;d<i.length;d++)c=i[d](c);var h=t((function(e){c.initializeInstanceElements(e,f.elements)}),r),f=c.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===s.key&&e.placement===s.placement},i=0;i<e.length;i++){var n,s=e[i];if("method"===s.kind&&(n=t.find(r)))if(l(s.descriptor)||l(n.descriptor)){if(a(s)||a(n))throw new ReferenceError("Duplicated methods ("+s.key+") can't be decorated.");n.descriptor=s.descriptor}else{if(a(s)){if(a(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+s.key+").");n.decorators=s.decorators}o(s,n)}else t.push(s)}return t}(h.d.map(s)),e);c.initializeClassElements(h.F,f.elements),c.runClassFinishers(h.F,f.finishers)}([(0,r(33310).Mo)("ha-input-helper-text")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"method",key:"render",value:function(){return i.dy`<slot></slot>`}},{kind:"field",static:!0,key:"styles",value:()=>i.iv`
    :host {
      display: block;
      color: var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6));
      font-size: 0.75rem;
      padding-left: 16px;
      padding-right: 16px;
    }
  `}]}}),i.oi)},3542:(e,t,r)=>{r.a(e,(async e=>{r.r(t);r(53268),r(12730);var i=r(59401),n=r(59281),s=r(27088),o=r(70390),a=r(83008),l=r(47538),c=r(79021),d=r(37500),h=r(33310),f=r(349),u=r(58831),p=r(91741),y=r(83849),m=r(15493),v=r(87744),g=r(77243),k=(r(31206),r(39143)),b=(r(10983),r(48932),r(63681),r(57292)),_=r(74186),w=r(58763),E=(r(27849),r(73826)),D=r(11654),P=e([w,k,g]);function S(){S=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var s="static"===n?e:r;this.defineClassElement(s,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!A(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var s=this.decorateConstructor(r,t);return i.push.apply(i,s.finishers),s.finishers=i,s},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,s=n.length-1;s>=0;s--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[s])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),s=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==s.finisher&&r.push(s.finisher),void 0!==s.elements){e=s.elements;for(var o=0;o<e.length-1;o++)for(var a=o+1;a<e.length;a++)if(e[o].key===e[a].key&&e[o].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return V(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?V(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=O(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var s={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),s.initializer=e.initializer),s},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:z(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=z(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function x(e){var t,r=O(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function C(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function A(e){return e.decorators&&e.decorators.length}function T(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function z(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function O(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function V(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function $(e,t,r){return $="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=I(e)););return e}(e,t);if(i){var n=Object.getOwnPropertyDescriptor(i,t);return n.get?n.get.call(r):n.value}},$(e,t,r||e)}function I(e){return I=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},I(e)}[w,k,g]=P.then?await P:P;let j=function(e,t,r,i){var n=S();if(i)for(var s=0;s<i.length;s++)n=i[s](n);var o=t((function(e){n.initializeInstanceElements(e,a.elements)}),r),a=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===s.key&&e.placement===s.placement},i=0;i<e.length;i++){var n,s=e[i];if("method"===s.kind&&(n=t.find(r)))if(T(s.descriptor)||T(n.descriptor)){if(A(s)||A(n))throw new ReferenceError("Duplicated methods ("+s.key+") can't be decorated.");n.descriptor=s.descriptor}else{if(A(s)){if(A(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+s.key+").");n.decorators=s.decorators}C(s,n)}else t.push(s)}return t}(o.d.map(x)),e);return n.initializeClassElements(o.F,a.elements),n.runClassFinishers(o.F,a.finishers)}(null,(function(e,t){class r extends t{constructor(){super(),e(this);const t=new Date;t.setHours(t.getHours()-2,0,0,0),this._startDate=t;const r=new Date;r.setHours(r.getHours()+1,0,0,0),this._endDate=r}}return{F:r,d:[{kind:"field",decorators:[(0,h.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,h.Cb)({reflect:!0,type:Boolean})],key:"narrow",value:void 0},{kind:"field",decorators:[(0,h.Cb)({reflect:!0,type:Boolean})],key:"rtl",value:()=>!1},{kind:"field",decorators:[(0,h.SB)()],key:"_startDate",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_endDate",value:void 0},{kind:"field",decorators:[(0,f.m)("historyPickedValue",!0,!1)],key:"_targetPickerValue",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_isLoading",value:()=>!1},{kind:"field",decorators:[(0,h.SB)()],key:"_stateHistory",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_ranges",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_devices",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_entities",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_stateEntities",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_deviceIdToEntities",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_areaIdToEntities",value:void 0},{kind:"field",decorators:[(0,h.SB)()],key:"_areaIdToDevices",value:void 0},{kind:"method",key:"hassSubscribe",value:function(){return[(0,_.LM)(this.hass.connection,(e=>{this._entities=e.reduce(((e,t)=>(e[t.entity_id]=t,e)),{}),this._deviceIdToEntities=e.reduce(((e,t)=>{if(!t.device_id)return e;let r=e[t.device_id];return void 0===r&&(r=[],e[t.device_id]=r),r.push(t),e}),{}),this._areaIdToEntities=e.reduce(((e,t)=>{if(!t.area_id)return e;let r=e[t.area_id];return void 0===r&&(r=[],e[t.area_id]=r),r.push(t),e}),{})})),(0,b.q4)(this.hass.connection,(e=>{this._devices=e.reduce(((e,t)=>(e[t.id]=t,e)),{}),this._areaIdToDevices=e.reduce(((e,t)=>{if(!t.area_id)return e;let r=e[t.area_id];return void 0===r&&(r=[],e[t.area_id]=r),r.push(t),e}),{})}))]}},{kind:"method",key:"render",value:function(){return d.dy`
      <ha-app-layout>
        <app-header slot="header" fixed>
          <app-toolbar>
            <ha-menu-button
              .hass=${this.hass}
              .narrow=${this.narrow}
            ></ha-menu-button>
            <div main-title>${this.hass.localize("panel.history")}</div>
            ${this._targetPickerValue?d.dy`
                  <ha-icon-button
                    @click=${this._removeAll}
                    .disabled=${this._isLoading}
                    .path=${"M14,4H4V14H2V4A2,2 0 0,1 4,2H14V4M18,6H8A2,2 0 0,0 6,8V18H8V8H18V6M22,12V20A2,2 0 0,1 20,22H12A2,2 0 0,1 10,20V12A2,2 0 0,1 12,10H20A2,2 0 0,1 22,12M20,15H12V17H20V15Z"}
                    .label=${this.hass.localize("ui.panel.history.remove_all")}
                  ></ha-icon-button>
                `:""}
            <ha-icon-button
              @click=${this._getHistory}
              .disabled=${this._isLoading}
              .path=${"M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"}
              .label=${this.hass.localize("ui.common.refresh")}
            ></ha-icon-button>
          </app-toolbar>
        </app-header>

        <div class="flex content">
          <div class="filters flex layout horizontal narrow-wrap">
            <ha-date-range-picker
              .hass=${this.hass}
              ?disabled=${this._isLoading}
              .startDate=${this._startDate}
              .endDate=${this._endDate}
              .ranges=${this._ranges}
              @change=${this._dateRangeChanged}
            ></ha-date-range-picker>
            <ha-target-picker
              .hass=${this.hass}
              .value=${this._targetPickerValue}
              .disabled=${this._isLoading}
              horizontal
              @value-changed=${this._entitiesChanged}
            ></ha-target-picker>
          </div>
          ${this._isLoading?d.dy`<div class="progress-wrapper">
                <ha-circular-progress
                  active
                  alt=${this.hass.localize("ui.common.loading")}
                ></ha-circular-progress>
              </div>`:this._targetPickerValue?d.dy`
                <state-history-charts
                  .hass=${this.hass}
                  .historyData=${this._stateHistory}
                  .endTime=${this._endDate}
                  no-single
                >
                </state-history-charts>
              `:d.dy`<div class="start-search">
                ${this.hass.localize("ui.panel.history.start_search")}
              </div>`}
        </div>
      </ha-app-layout>
    `}},{kind:"method",key:"firstUpdated",value:function(e){$(I(r.prototype),"firstUpdated",this).call(this,e);const t=new Date,d=(0,i.Z)(t),h=(0,n.Z)(t);this._ranges={[this.hass.localize("ui.components.date-range-picker.ranges.today")]:[(0,s.Z)(),(0,o.Z)()],[this.hass.localize("ui.components.date-range-picker.ranges.yesterday")]:[(0,a.Z)(),(0,l.Z)()],[this.hass.localize("ui.components.date-range-picker.ranges.this_week")]:[d,h],[this.hass.localize("ui.components.date-range-picker.ranges.last_week")]:[(0,c.Z)(d,-7),(0,c.Z)(h,-7)]};const f=(0,m.io)("entity_id");if(f){const e=f.split(",");this._targetPickerValue={entity_id:e}}const u=(0,m.io)("start_date");u&&(this._startDate=new Date(u));const p=(0,m.io)("end_date");p&&(this._endDate=new Date(p))}},{kind:"method",key:"updated",value:function(e){if(this._targetPickerValue&&(e.has("_startDate")||e.has("_endDate")||e.has("_targetPickerValue")||!this._stateHistory&&(e.has("_entities")||e.has("_devices")||e.has("_stateEntities")||e.has("_deviceIdToEntities")||e.has("_areaIdToEntities")||e.has("_areaIdToDevices")))&&this._getHistory(),!e.has("hass")&&!e.has("_entities"))return;const t=e.get("hass");if(t&&t.language===this.hass.language||(this.rtl=(0,v.HE)(this.hass)),this._entities){const e={},t=new Set(Object.keys(this._entities));for(const r of Object.keys(this.hass.states))t.has(r)||(e[r]={name:(0,p.C)(this.hass.states[r]),entity_id:r,platform:(0,u.M)(r),disabled_by:null,hidden_by:null,area_id:null,config_entry_id:null,device_id:null,icon:null,entity_category:null});this._stateEntities=e}}},{kind:"method",key:"_removeAll",value:function(){this._targetPickerValue=void 0,this._updatePath()}},{kind:"method",key:"_getHistory",value:async function(){this._isLoading=!0;const e=this._getEntityIds();if(!e.length)return void(this._stateHistory=void 0);const t=await(0,w.iz)(this.hass,this._startDate,this._endDate,e);this._stateHistory=(0,w.Nu)(this.hass,t,this.hass.localize),this._isLoading=!1}},{kind:"method",key:"_getEntityIds",value:function(){if(void 0===this._targetPickerValue||void 0===this._entities||void 0===this._stateEntities||void 0===this._devices||void 0===this._deviceIdToEntities||void 0===this._areaIdToEntities||void 0===this._areaIdToDevices)return[];const e=new Set;let{area_id:t,device_id:r,entity_id:i}=this._targetPickerValue;if(void 0!==t){t="string"==typeof t?[t]:t;for(const r of t){const t=this._areaIdToEntities[r];if(!t)continue;for(const r of t)null===r.entity_category&&e.add(r.entity_id);const i=this._areaIdToDevices[r];if(void 0!==i)for(const t of i){const i=this._deviceIdToEntities[t.id];for(const t of i)t.area_id&&t.area_id!==r||null!==t.entity_category||e.add(t.entity_id)}}}if(void 0!==r){r="string"==typeof r?[r]:r;for(const t of r){const r=this._deviceIdToEntities[t];if(r)for(const t of r)null===t.entity_category&&e.add(t.entity_id)}}if(void 0!==i){i="string"==typeof i?[i]:i;for(const t of i)e.add(t)}return[...e]}},{kind:"method",key:"_dateRangeChanged",value:function(e){this._startDate=e.detail.startDate;const t=e.detail.endDate;0===t.getHours()&&0===t.getMinutes()&&(t.setDate(t.getDate()+1),t.setMilliseconds(t.getMilliseconds()-1)),this._endDate=t,this._updatePath()}},{kind:"method",key:"_entitiesChanged",value:function(e){this._targetPickerValue=e.detail.value,this._updatePath()}},{kind:"method",key:"_updatePath",value:function(){const e={};this._targetPickerValue&&(e.entity_id=this._getEntityIds().join(",")),this._startDate&&(e.start_date=this._startDate.toISOString()),this._endDate&&(e.end_date=this._endDate.toISOString()),(0,y.c)(`/history?${(0,m.ou)(e)}`,{replace:!0})}},{kind:"get",static:!0,key:"styles",value:function(){return[D.Qx,d.iv`
        .content {
          padding: 0 16px 16px;
        }

        state-history-charts {
          height: calc(100vh - 136px);
        }

        :host([narrow]) state-history-charts {
          height: calc(100vh - 198px);
        }

        .progress-wrapper {
          height: calc(100vh - 136px);
        }

        :host([narrow]) .progress-wrapper {
          height: calc(100vh - 198px);
        }

        :host([virtualize]) {
          height: 100%;
        }

        :host([narrow]) .narrow-wrap {
          flex-wrap: wrap;
        }

        .horizontal {
          align-items: center;
        }

        :host(:not([narrow])) .selector-padding {
          padding-left: 32px;
        }

        .progress-wrapper {
          position: relative;
        }

        .filters {
          display: flex;
          align-items: flex-start;
          padding: 8px 16px 0;
        }

        :host([narrow]) .filters {
          flex-wrap: wrap;
        }

        ha-date-range-picker {
          margin-right: 16px;
          margin-inline-end: 16px;
          margin-inline-start: initial;
          max-width: 100%;
          direction: var(--direction);
        }

        :host([narrow]) ha-date-range-picker {
          margin-right: 0;
          margin-inline-end: 0;
          margin-inline-start: initial;
          direction: var(--direction);
        }

        ha-circular-progress {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
        }

        ha-entity-picker {
          display: inline-block;
          flex-grow: 1;
          max-width: 400px;
        }

        :host([narrow]) ha-entity-picker {
          max-width: none;
          width: 100%;
        }

        .start-search {
          padding-top: 16px;
          text-align: center;
          color: var(--secondary-text-color);
        }
      `]}}]}}),(0,E.f)(d.oi));customElements.define("ha-panel-history",j)}))}}]);
//# sourceMappingURL=7886a90d.js.map