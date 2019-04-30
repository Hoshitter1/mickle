
  Vue.directive('scroll', {
  inserted: function (el, binding) {
    let f = function (evt) {
      if (binding.value(evt, el)) {
        window.removeEventListener('scroll', f)
      }
    }
    window.addEventListener('scroll', f)
  }
})

// main app
new Vue({
  el: '#app',
  methods: {
    handleScroll: function (evt, el) {
      if (window.scrollY > 50) {
        el.setAttribute(
          'style',
          'opacity: 1; transform: translate3d(0, -30px, 0)'
        )
      }
      return window.scrollY > 100
    }
  }
})

new Vue({
  el: '#app-3',
  methods: {
    handleScroll: function (evt, el) {
      if (window.scrollY > 100) {
        el.setAttribute(
          'style',
          'opacity: 1; transform: translate3d(0, -30px, 0)'
        )
      }
      return window.scrollY > 150
    }
  }
})

 new Vue({
  el: '#app-2',
  data: {
    message: 'Hello World!',
  },
});
