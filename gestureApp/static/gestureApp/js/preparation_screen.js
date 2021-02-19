// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
    el: '#app',
    data: function () {
        return {
            exp_code: JSON.parse(document.getElementById('exp_code').textContent),
        }
    },
    template: `
      <PrepScreen
        v-bind="getPrepScreenObj"
      />
      `,
    components: {
        'PrepScreen': httpVueLoader('/static/gestureApp/js/components/PreparationScreen.vue'),
    },
    computed: {
        getPrepScreenObj() {
            return {
                exp_code: this.exp_code,
            }
        }
    },
    methods: {
    },
    mounted() {
    },
});

