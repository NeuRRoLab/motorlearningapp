// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      experiment_code: null,
      is_experiment_published: false,
      experiment_name: null,
      with_practice_trials: false,
      practice_trials: null,
      practice_is_random_sequence: true,
      practice_seq_length: null,
      practice_sequence: "",
      practice_trial_time: null,
      practice_rest_time: null,
      with_feedback: true,
      experiment_blocks: [
        {
          block_id: null,
          sequence: null,
          max_time_per_trial: null,
          resting_time: null,
          block_type: null,
          num_trials: null,
          max_time: null,
          sec_until_next: 0,
          is_random_sequence: false,
          seq_length: null,
          num_repetitions: 1,
        },
      ],
      block_types: [
        { value: null, text: "Please select a block type" },
        { value: "max_time", text: "Maximum time" },
        { value: "num_trials", text: "Number of trials" },
      ],
      // Whether we are creating or editing an experiment
      editing: false,
    }
  },
  template: `
      <div>
        <ExperimentForm v-bind="getExperimentFormData"
          @submit-experiment="submitExperiment"
        />
      </div>
      `,
  components: {
    'ExperimentForm': httpVueLoader('/static/gestureApp/js/components/ExperimentForm.vue'),
  },
  computed: {
    getExperimentFormData() {
      return {
        experiment_code: this.experiment_code,
        editing: this.editing,
        published: this.is_experiment_published,

        prop_experiment_name: this.experiment_name,
        prop_with_practice_trials: this.with_practice_trials,
        prop_practice_trials: this.practice_trials,
        prop_practice_is_random_sequence: this.practice_is_random_sequence,
        prop_practice_seq_length: this.practice_seq_length,
        prop_practice_sequence: this.practice_sequence,
        prop_practice_trial_time: this.practice_trial_time,
        prop_practice_rest_time: this.practice_rest_time,
        prop_experiment_blocks: this.experiment_blocks,
        prop_block_types: this.block_types,
        prop_with_feedback: this.with_feedback,
      }
    }
  },
  methods: {
    submitExperiment(name, with_practice_trials, practice_trials, practice_is_random_sequence, practice_seq_length, practice_sequence, practice_trial_time, practice_rest_time, blocks, video_file, consent_file, with_feedback) {
      let obj = {
        code: this.experiment_code,
        name: name,
        practice_trials: practice_trials,
        blocks: blocks,
        with_practice_trials: with_practice_trials,
        practice_is_random_seq: practice_is_random_sequence,
        practice_seq_length: practice_seq_length,
        practice_seq: practice_sequence,
        practice_trial_time: practice_trial_time,
        practice_rest_time: practice_rest_time,
        with_feedback: with_feedback,
      }
      let formData = new FormData();
      formData.append("consent", consent_file);
      formData.append("video", video_file);
      if (!this.editing)
        axios.post('/profile/create_experiment', obj).then(response => {
          axios.post(`/profile/experiment/upload_files/${response.data.code}/`, formData)
            .then(response =>
              window.location.href = '/profile'
            );
        })
      else {

        axios.post(`/profile/experiment/edit/${this.experiment_code}/`, obj).then(response => {
          console.log(response);
          axios.post(`/profile/experiment/upload_files/${this.experiment_code}/`, formData)
            .then(response =>
              window.location.href = '/profile'
            );
        })
      }
    },
  },
  created() {
    // TODO: Read from HTML if existent
    if (document.getElementById("experiment") !== null && document.getElementById("blocks") !== null) {
      // If no experiment data is available, then we are creating a new experiment
      if (!JSON.parse(document.getElementById('experiment').textContent) || !JSON.parse(document.getElementById('blocks').textContent))
        return;
      this.editing = true;
      html_experiment = JSON.parse(document.getElementById('experiment').textContent);
      this.experiment_code = html_experiment.code;
      this.is_experiment_published = html_experiment.published;
      this.experiment_name = html_experiment.name;
      this.with_practice_trials = html_experiment.with_practice_trials;
      this.practice_trials = html_experiment.num_practice_trials;
      this.practice_is_random_sequence = html_experiment.practice_is_random_seq;
      this.practice_seq_length = html_experiment.practice_seq_length;
      this.practice_sequence = html_experiment.practice_seq;
      this.practice_trial_time = html_experiment.practice_trial_time;
      this.practice_rest_time = html_experiment.practice_rest_time;
      this.with_feedback = html_experiment.with_feedback;

      html_blocks = JSON.parse(document.getElementById('blocks').textContent);
      if (html_blocks !== undefined && html_blocks.length != 0) {
        this.experiment_blocks = [];
        html_blocks.forEach(block => {
          this.experiment_blocks.push({
            block_id: block.id,
            sequence: block.sequence,
            max_time_per_trial: block.max_time_per_trial,
            resting_time: block.resting_time,
            block_type: block.type,
            num_trials: block.num_trials,
            max_time: block.max_time,
            sec_until_next: block.sec_until_next,
            is_random_sequence: block.is_random,
            seq_length: block.seq_length,
            num_repetitions: 1,
          });
        });
      }
    }
  },
});

