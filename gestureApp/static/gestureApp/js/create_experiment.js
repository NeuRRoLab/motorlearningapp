// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
  el: '#app',
  data: function () {
    return {
    }
  },
  template: `
      <div>
        <ExperimentForm
          @submit-experiment="submitExperiment"
        />
      </div>
      `,
  components: {
    'ExperimentForm': httpVueLoader('/static/gestureApp/js/components/ExperimentForm.vue'),
  },
  computed: {
  },
  methods: {
    submitExperiment(name, practice_trials, blocks) {
      let obj = { name: name, practice_trials: practice_trials, blocks: blocks }
      axios.post('/profile/create_experiment', obj).then(response => {
        console.log(response);
        window.location.href = '/profile';
      })
    },
  },
  created: function () {

  },
});

