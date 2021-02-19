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
    submitExperiment(name, with_practice_trials, practice_trials, practice_is_random_sequence, practice_seq_length, practice_sequence, practice_trial_time, practice_rest_time, blocks) {
      let obj = {
        name: name,
        practice_trials: practice_trials,
        blocks: blocks,
        with_practice_trials: with_practice_trials,
        practice_is_random_seq: practice_is_random_sequence,
        practice_seq_length: practice_seq_length,
        practice_seq: practice_sequence,
        practice_trial_time: practice_trial_time,
        practice_rest_time: practice_rest_time,
      }
      axios.post('/profile/create_experiment', obj).then(response => {
        console.log(response);
        window.location.href = '/profile';
      })
    },
  },
  created: function () {

  },
});

