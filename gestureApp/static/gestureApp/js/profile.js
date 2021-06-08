// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      current_user: {},
      studies: [],
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
        @new-group="newGroup"
        @disable-experiment="disableExperiment"
        @enable-experiment="enableExperiment"
        @delete-experiment="deleteExperiment"
        @duplicate-experiment="duplicateExperiment"
        @publish-study="publishStudy"
        @disable-study="disableStudy"
        @enable-study="enableStudy"
        @delete-study="deleteStudy"
        @duplicate-study="duplicateStudy"
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
        studies: this.studies
      }
    }
  },
  methods: {
    getCurrentUser() {
      axios.get('/api/current_user').then(response => {
        this.current_user = response.data;
      })
    },
    getUserStudies() {
      axios.get('/api/user_studies').then(response => {
        this.studies = response.data.studies;
      })
    },
    newGroup(name, study_code) {
      axios.post(`/api/group/new/`, { name: name, study: study_code }).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Group '${name}' successfully created in study ${study_code}`,
          type: 'success',
        });
      });
    },
    enableExperiment(code) {
      axios.post(`/api/experiment/enable/${code}/`).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully enabled`,
          type: 'success',
        });
      });
    },
    disableExperiment(code) {
      axios.post(`/api/experiment/disable/${code}/`).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully disabled`,
          type: 'success',
        });
      });
    },
    deleteExperiment(code) {
      if (prompt(`Are you sure you want to delete Experiment ${code} and all its data? Enter the experiment code to confirm the deletion`) === code) {
        axios.post(`/api/experiment/delete/${code}/`).then(response => {
          this.getUserStudies();
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
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Experiment ${code} successfully duplicated`,
          type: 'success',
        });
      });
    },
    publishStudy(code) {
      if (confirm("Publishing the study will forbid any future edits in its experiments and will discard the testing data. Are you sure you want to proceed?")) {
        axios.post(`/api/study/publish/${code}/`).then(response => {
          this.getUserStudies();
          this.$notify({
            group: 'alerts',
            title: `Study ${code} successfully published`,
            type: 'success',
          });
        });
      }
    },
    enableStudy(code) {
      axios.post(`/api/study/enable/${code}/`).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Study ${code} successfully enabled`,
          type: 'success',
        });
      });
    },
    disableStudy(code) {
      axios.post(`/api/study/disable/${code}/`).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Study ${code} successfully disabled`,
          type: 'success',
        });
      });
    },
    deleteStudy(code) {
      if (prompt(`Are you sure you want to delete Study ${code} and all its data? Enter the study code to confirm the deletion`) === code) {
        axios.post(`/api/study/delete/${code}/`).then(response => {
          this.getUserStudies();
          this.$notify({
            group: 'alerts',
            title: `Study ${code} successfully deleted`,
            type: 'success',
          });
        });
      }
    },
    duplicateStudy(code) {
      axios.post(`/api/study/duplicate/${code}/`).then(response => {
        this.getUserStudies();
        this.$notify({
          group: 'alerts',
          title: `Study ${code} successfully duplicated`,
          type: 'success',
        });
      });
    },
  },
  mounted() {
    this.getCurrentUser();
    this.getUserStudies();
  },
});

