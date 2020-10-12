// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
    el: '#app',
    data: function () {
        return {
        }
      },
    template:`
      `,
    components: {
        'Experiment': httpVueLoader('/static/gestureApp/js/components/Experiment.vue'),
    },
    computed: {
    },
    methods: {
    },
    created: function () {
      this.experiment = JSON.parse(document.getElementById('experiment').textContent);
      this.blocks = JSON.parse(document.getElementById('blocks').textContent);
      
    },
  });

