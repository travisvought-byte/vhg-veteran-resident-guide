'use strict';
(() => {
 const params = new URLSearchParams(location.search);
 const state = (params.get('state') || 'OH').toUpperCase();
 if (state === 'OH') location.replace('https://www.ohiomom.org/family-guide.html' + location.search + location.hash);
})();
