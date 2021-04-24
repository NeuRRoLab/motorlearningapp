<template>
  <div class="container">
    <h1 v-if="!editing" class="text-center">Create new Experiment</h1>
    <h1 v-else-if="published" class="text-center">View experiment {{ experiment_code }}</h1>
    <h1 v-else class="text-center">Edit experiment {{ experiment_code }}</h1>
    <b-form @submit="onSubmitExperiment" @reset="resetExperiment">
      <b-form-group label="Experiment Name:" label-for="name">
        <b-form-input
          name="name"
          id="name"
          v-model="experiment_name"
          type="text"
          required
          placeholder="Name"
          :disabled="published"
        ></b-form-input>
      </b-form-group>
      <b-form-group label="Instructions video:" label-for="instructions-video">
        <b-form-file
          accept=".mp4"
          id="instructions-video"
          v-model="video_file"
          :state="Boolean(video_file)"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
          required
        ></b-form-file>
      </b-form-group>
      <b-form-group label="Consent form:" label-for="consent-form">
        <b-form-file
          accept=".pdf"
          id="consent-form"
          v-model="consent_file"
          :state="Boolean(consent_file)"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
          required
        ></b-form-file>
      </b-form-group>
      <b-form-group>
        <b-form-checkbox
          switch
          id="checkbox-practice-trials"
          v-model="with_practice_trials"
          name="checkbox-practice-trials"
          :disabled="published"
        >
          Practice Trials
        </b-form-checkbox>
      </b-form-group>
      <template v-if="with_practice_trials">
        <div class="form-row">
          <b-form-group
            class="col"
            label="Number of practice trials:"
            label-for="practice-trials"
          >
            <b-form-input
              id="practice-trials"
              v-model.number="practice_trials"
              type="number"
              required
              placeholder=""
              :disabled="published"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            class="col"
            label="Maximum time (s) per trial:"
            :label-for="'prac-max-time'"
          >
            <b-form-input
              name="name"
              :id="'prac-max-time'"
              v-model.number="practice_trial_time"
              type="number"
              step="0.1"
              required
              placeholder="Maximum time per trial"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            class="col"
            label="Resting time (s):"
            :label-for="'prac-resting-'"
          >
            <b-form-input
              name="name"
              :id="'prac-resting-'"
              v-model.number="practice_rest_time"
              type="number"
              step="0.1"
              required
              placeholder="Resting time between trials"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col-4"
            label="Practice Trials Sequence:"
            label-for="practice-seq"
          >
            <b-form-input
              id="practice-seq"
              v-model="practice_sequence"
              type="text"
              required
              placeholder=""
              :disabled="practice_is_random_sequence || published"
            ></b-form-input>
            <b-form-checkbox
              switch
              v-model="practice_is_random_sequence"
              name="checkbox-random_seq"
              :disabled="published"
            >
              Random Sequence
            </b-form-checkbox>
          </b-form-group>
          <b-form-group
            class="col-2"
            v-if="practice_is_random_sequence"
            label="Sequence length:"
            label-for="seq-length"
          >
            <b-form-input
              id="seq-length"
              v-model.number="practice_seq_length"
              type="number"
              required
              placeholder=""
              :disabled="published"
            ></b-form-input>
        </div>
      </template>
      <h5>Blocks:</h5>
      <div
        class="block-form"
        v-for="(block, index) in experiment_blocks"
        :key="index"
      >
        <div class="form-row">
          <b-form-group
            class="col"
            label="Sequence:"
            :label-for="'sequence-' + index"
          >
            <b-form-input
              name="name"
              :id="'sequence-' + index"
              v-model="block.sequence"
              type="text"
              required
              placeholder="Sequence of characters"
              :disabled="block.is_random_sequence || published"
            ></b-form-input>
            <b-form-checkbox switch v-model="block.is_random_sequence" :disabled="published">
              Random Sequence
            </b-form-checkbox>
          </b-form-group>
          <b-form-group
            class="col"
            label="Maximum time (s) per trial:"
            :label-for="'max-time-' + index"
          >
            <b-form-input
              name="name"
              :id="'max-time-' + index"
              v-model.number="block.max_time_per_trial"
              type="number"
              step="0.1"
              required
              placeholder="Maximum time per trial"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            class="col"
            label="Resting time (s):"
            :label-for="'resting-' + index"
          >
            <b-form-input
              name="name"
              :id="'resting-' + index"
              v-model.number="block.resting_time"
              type="number"
              step="0.1"
              required
              placeholder="Resting time between trials"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row" v-if="block.is_random_sequence">
          <b-form-group
            class="col-3"
            label="Sequence length:"
            :label-for="'block-seq-length-' + index"
          >
            <b-form-input
              name="name"
              :id="'block-seq-length-' + index"
              v-model.number="block.seq_length"
              type="number"
              required
              placeholder="Random sequence length"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col-6"
            label="Block type:"
            :label-for="'block-type' + index"
          >
            <b-form-select
              :id="'block-type' + index"
              v-model="block.block_type"
              :options="block_types"
              required
              :disabled="published"
            ></b-form-select>
          </b-form-group>
          <b-form-group
            v-if="block.block_type === 'num_trials'"
            class="col"
            label="Number of Trials:"
            :label-for="'num-trials' + index"
          >
            <b-form-input
              :id="'num-trials-' + index"
              v-model.number="block.num_trials"
              type="number"
              required
              placeholder="Total number of trials"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            v-if="block.block_type === 'max_time'"
            class="col"
            label="Maximum time (s):"
            :label-for="'max-time' + index"
          >
            <b-form-input
              :id="'max-time-' + index"
              v-model.number="block.max_time"
              type="number"
              step="0.1"
              required
              placeholder="Maximum time (seconds)"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col-6"
            label="Resting time (seconds) until next block:"
            :label-for="'betw-blocks-' + index"
            description="Set to 0 if you want the next block to start immediately"
          >
            <b-form-input
              name="name"
              :id="'betw-blocks-' + index"
              v-model.number="block.sec_until_next"
              type="number"
              step="0.1"
              required
              placeholder="Seconds until next block"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col-6"
            label="Repeat block:"
            :label-for="'rep-blocks-' + index"
            description="Set to greater than 1 if you want N identical blocks"
          >
            <b-form-input
              name="rep-blocks"
              :id="'rep-blocks-' + index"
              v-model.number="block.num_repetitions"
              type="number"
              step="1"
              min="1"
              required
              placeholder="Number of repetitions"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <button @click="removeBlock" class="btn btn-link text-danger" :disabled="published">
            Remove block
          </button>
        </div>
      </div>
      <button @click="addBlock" class="btn btn-link" :disabled="published">Add block</button>
      <div class="form-row">
        <div class="col">
          <b-button type="reset" class="btn btn-block" variant="danger" :disabled="published"
            >Reset</b-button
          >
        </div>
        <div class="col">
          <b-button type="submit" class="btn btn-block" variant="primary" :disabled="published"
            >Submit</b-button
          >
        </div>
      </div>
    </b-form>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      experiment_name: this.prop_experiment_name,
      with_practice_trials: this.prop_with_practice_trials,
      practice_trials: this.prop_practice_trials,
      practice_is_random_sequence: this.prop_practice_is_random_sequence,
      practice_seq_length: this.prop_practice_seq_length,
      practice_sequence: this.prop_practice_sequence,
      practice_trial_time: this.prop_practice_trial_time,
      practice_rest_time: this.prop_practice_rest_time,
      experiment_blocks: this.prop_experiment_blocks,
      block_types: this.prop_block_types,
      video_file: null,
      consent_file: null,
    };
  },
  props: {
    experiment_code: String,
    editing: Boolean,
    published: Boolean,
    prop_experiment_name: String,
    prop_with_practice_trials: Boolean,
    prop_practice_trials: Number,
    prop_practice_is_random_sequence: Boolean,
    prop_practice_seq_length: Number,
    prop_practice_sequence: String,
    prop_practice_trial_time: Number,
    prop_practice_rest_time: Number,
    prop_experiment_blocks: Array,
    prop_block_types: Array,
  },
  mounted: function () {},
  components: {
    "nav-bar": httpVueLoader("/static/gestureApp/js/components/NavBar.vue"),
  },
  computed: {},
  watch: {},
  methods: {
    addBlock() {
      this.experiment_blocks.push({
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
      });
    },
    removeBlock(index) {
      this.experiment_blocks.splice(index, 1);
    },
    onSubmitExperiment(evt) {
      evt.preventDefault();

      this.$emit(
        "submit-experiment",
        this.experiment_name,
        this.with_practice_trials,
        this.practice_trials,
        this.practice_is_random_sequence,
        this.practice_seq_length,
        this.practice_sequence,
        this.practice_trial_time,
        this.practice_rest_time,
        this.experiment_blocks,
        this.video_file,
        this.consent_file,
      );
    },
    resetExperiment(evt) {
      evt.preventDefault();
      console.log(this.experiment_blocks);

      this.experiment_name = null;
      this.experiment_blocks = [];
      this.addBlock();
    },
  },
};
</script>

<style scoped>
.block-form {
  border: 1px solid lightgray;
  padding: 10px;
}
.block-form + .block-form {
  margin-top: 10px;
}
</style>
