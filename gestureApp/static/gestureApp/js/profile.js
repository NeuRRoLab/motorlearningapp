// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
    el: '#app',
    data: function () {
        return {
          current_user: {},
          experiments: [],
        }
      },
    template:`
      <Profile
        v-bind="getProfileObj"
      />
      `,
    components: {
        'Profile': httpVueLoader('/static/gestureApp/js/components/Profile.vue'),
    },
    computed: {
      getProfileObj() {
        return {
          current_user: this.current_user,
          experiments: this.experiments,
        }
      }
    },
    methods: {
      getCurrentUser() {
          axios.get('/api/current_user').then(response => {
              this.current_user = response.data;
          })
      },
      getUserExperiments() {
        axios.get('/api/user_experiments').then(response => {
            this.experiments = response.data.experiments;
        })
      },
    },
    mounted() {
      this.getCurrentUser();
      this.getUserExperiments();
    },
  });

