var app = new Vue({
    el: '#app',
    data: function () {
        return {
        }
      },
    template:`
      <Home
        v-bind="getHomeObj"

      />
      `,
    components: {
        'Home': httpVueLoader('/static/gestureApp/js/components/Home.vue'),
    },
    computed: {
      getHomeObj: function () {
        return {
          hola: 'hola'
        }
      }
    },
    methods: {
    },
    created: function () {     
    },
  });

