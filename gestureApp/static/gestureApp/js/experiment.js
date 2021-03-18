// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

Vue.component('countdown', VueCountdown);

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      experiment: '',
      blocks: [],
      with_practice_trials: false,
      num_practice_trials: 0,
      practice_is_random_seq: false,
      practice_seq: null
    }
  },
  template: `
      <Experiment ref="experiment"
        v-bind="getExperimentObj"
        @send-data="sendData"
      />
      `,
  components: {
    'Experiment': httpVueLoader('/static/gestureApp/js/components/Experiment.vue'),
  },
  computed: {
    getExperimentObj: function () {
      return {
        experiment: this.experiment,
        blocks: this.blocks,
        with_practice_trials: this.with_practice_trials,
        num_practice_trials: this.num_practice_trials,
        practice_is_random_seq: this.practice_is_random_seq,
        practice_seq: this.practice_seq
      }
    },
  },
  methods: {
    sendData: function (experiment_blocks) {
      console.log(this.$refs.experiment)
      console.log(experiment_blocks);
      // console.log(this.)
      axios.post('/api/create_trials', {
        'experiment_trials': JSON.stringify(experiment_blocks),
        'experiment': this.experiment.code
      }
      ).then(response => {
        console.log(response);
        this.$refs.experiment.$notify({
          group: 'alerts',
          title: 'Success sending data',
          type: 'success',
        });
        // this.$refs.experiment.experiment_finished = false;
        this.$refs.experiment.experiment_started = false;
      }
      ).catch(error => {
        this.$refs.experiment.$notify({
          group: 'alerts',
          title: 'Error sending data',
          text: `Please try again. ${error}`,
          type: 'error',
        });
      })
    }
  },
  created: function () {
    this.experiment = JSON.parse(document.getElementById('experiment').textContent);
    this.blocks = JSON.parse(document.getElementById('blocks').textContent);
  },
});

