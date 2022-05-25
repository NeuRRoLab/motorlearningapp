// Parent script that manages the relationship between the Vue component and the Django API
// during the actual experiment

// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

// Countdown component
Vue.component('countdown', VueCountdown);

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      experiment: '',
      blocks: [],
      subject_code: null,
      // Some experiment properties
      with_practice_trials: false,
      num_practice_trials: 0,
      practice_is_random_seq: false,
      practice_seq: null,
      subject_code: null,
      // Data helper variables
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
      // Gets experiment object that will be sent to Vue component
      return {
        experiment: this.experiment,
        blocks: this.blocks,
        correctly_sent_data: this.correctly_sent_data,
        unsuccessful_data_sent_counter: this.unsuccessful_data_sent_counter,
        subject_code: this.subject_code,
      }
    },
  },
  methods: {
    sendData: function (experiment_blocks) {
      // Sends the data contained in the experiment blocks to the API
      if (!this.correctly_sent_data) {
        // Create POST request
        axios.post('/api/create_trials', {
          'experiment_trials': JSON.stringify(experiment_blocks),
          'experiment': this.experiment.code,
          'timezone_offset_sec': new Date().getTimezoneOffset() * 60,
          'subject_code': this.subject_code,
        }
        ).then(response => {
          // Notify the user that the data was sent correctly
          this.$refs.experiment.$notify({
            group: 'alerts',
            title: 'Success sending data to the server',
            type: 'success',
          });
          this.correctly_sent_data = true;
          this.$refs.experiment.experiment_started = false;
          this.subject_code = response.data.subject_code;
        }
        ).catch(error => {
          this.unsuccessful_data_sent_counter += 1;
          // Notify that there was an error sending the data to the server
          this.$refs.experiment.$notify({
            group: 'alerts',
            title: 'Error sending data to the server',
            text: `Please try again. ${error}`,
            type: 'error',
          });
        })
      }
    },
    sendSurvey(questionnaire) {
      // POST survey data
      axios.post(`/api/experiment/end_survey/${this.experiment.code}/`, {
        'questionnaire': questionnaire, 'subject_code': this.subject_code
      }
      ).then(response => window.location.href = "/");
    }
  },
  created: function () {
    this.experiment = JSON.parse(document.getElementById('experiment').textContent);
    this.blocks = JSON.parse(document.getElementById('blocks').textContent);
    this.subject_code = JSON.parse(document.getElementById('subject_code').textContent);
  },
});

