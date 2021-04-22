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
  template: `
  <div>
    <notifications
        group="alerts"
        position="top center"
        :max="2"
        :duration="6000"
    ></notifications>
      <Profile
        v-bind="getProfileObj"
        @publish-experiment="publishExperiment"
        @disable-experiment="disableExperiment"
        @enable-experiment="enableExperiment"
        @delete-experiment="deleteExperiment"
        @duplicate-experiment="duplicateExperiment"
      />
  </div>
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
      console.log("holaa")
      axios.get('/api/user_experiments').then(response => {
        this.experiments = response.data.experiments;
      })
    },
    publishExperiment(code) {
      axios.post(`/api/experiment/publish/${code}/`).then(response => {
        this.getUserExperiments();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully published`,
          type: 'success',
        });
      });
    },
    enableExperiment(code) {
      axios.post(`/api/experiment/enable/${code}/`).then(response => {
        this.getUserExperiments();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully enabled`,
          type: 'success',
        });
      });
    },
    disableExperiment(code) {
      axios.post(`/api/experiment/disable/${code}/`).then(response => {
        this.getUserExperiments();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully disabled`,
          type: 'success',
        });
      });
    },
    deleteExperiment(code) {
      if (confirm(`Are you sure you want to delete Experiment ${code} and all its data?`)) {
        axios.post(`/api/experiment/delete/${code}/`).then(response => {
          this.getUserExperiments();
          this.$notify({
            group: 'alerts',
            title: `Experiment ${code} successfully deleted`,
            type: 'success',
          });
        });
      }
    },
    duplicateExperiment(code) {
      axios.post(`/api/experiment/duplicate/${code}/`).then(response => {
        this.getUserExperiments();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully duplicated`,
          type: 'success',
        });
      });
    },
  },
  mounted() {
    this.getCurrentUser();
    this.getUserExperiments();
  },
});

