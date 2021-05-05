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
      practice_seq: null,
      subject_code: null,
      correctly_sent_data: false,
      unsuccessful_data_sent_counter: 0,
    }
  },
  template: `
      <Experiment ref="experiment"
        v-bind="getExperimentObj"
        @send-data="sendData"
        @end-survey="sendSurvey"
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
        correctly_sent_data: this.correctly_sent_data,
        unsuccessful_data_sent_counter: this.unsuccessful_data_sent_counter,
      }
    },
  },
  methods: {
    sendData: function (experiment_blocks) {
      console.log(this.$refs.experiment)
      console.log(experiment_blocks);
      // console.log(this.)
      if (!this.correctly_sent_data) {
        axios.post('/api/create_trials', {
          'experiment_trials': JSON.stringify(experiment_blocks),
          'experiment': this.experiment.code,
          'timezone_offset_sec': new Date().getTimezoneOffset() * 60,
        }
        ).then(response => {
          console.log(response);
          this.$refs.experiment.$notify({
            group: 'alerts',
            title: 'Success sending data',
            type: 'success',
          });
          this.correctly_sent_data = true;
          // this.$refs.experiment.experiment_finished = false;
          this.$refs.experiment.experiment_started = false;
          this.subject_code = response.data.subject_code;
        }
        ).catch(error => {
          this.unsuccessful_data_sent_counter += 1;
          this.$refs.experiment.$notify({
            group: 'alerts',
            title: 'Error sending data',
            text: `Please try again. ${error}`,
            type: 'error',
          });
        })
      }
    },
    sendSurvey(questionnaire) {
      axios.post(`/api/experiment/end_survey/${this.experiment.code}/`, { 'questionnaire': questionnaire, 'subject_code': this.subject_code }).then(response => window.location.href = "/");
    }
  },
  created: function () {
    this.experiment = JSON.parse(document.getElementById('experiment').textContent);
    this.blocks = JSON.parse(document.getElementById('blocks').textContent);
  },
});

