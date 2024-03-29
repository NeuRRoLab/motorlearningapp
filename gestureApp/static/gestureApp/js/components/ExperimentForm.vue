<!-- 
Manages the full form used to create new experiments. Includes all the possible options users have to customize
experiments, and includes a section to specify how blocks are going to look.

The same component is used in case the user wants to edit an existing experiment. The fields autofill by extracting
the experiment and block properties.

An experiment can only be edited if it hasn't been published yet. All fields will be disabled if it is published.
 -->
<template>
  <div class="container">
    <h1 v-if="!editing" class="text-center">Create new Experiment</h1>
    <h1 v-else-if="published" class="text-center">
      View experiment {{ experiment_code }}
    </h1>
    <h1 v-else class="text-center">Edit experiment {{ experiment_code }}</h1>
    <b-form @submit="onSubmitExperiment" @reset="resetExperiment">
      <!-- Study selector -->
      <b-form-group
        label="Study:"
        :label-for="'study'"
        :description="
          published
            ? ''
            : 'Only unpublished studies will be available. If you don\'t see any studies, you probably will need to create one first.'
        "
      >
        <!-- Get the name and code from all unpublished studies -->
        <b-form-select
          :id="'study'"
          v-model="study.code"
          :options="
            published
              ? [{ value: study.code, text: `${study.name} (${study.code})` }]
              : studies
                  .filter((study) => study.published === false)
                  .map((study) => {
                    return {
                      value: study.code,
                      text: `${study.name} (${study.code})`,
                    };
                  })
          "
          required
          :disabled="published"
        ></b-form-select>
      </b-form-group>
      <!-- Group selector -->
      <b-form-group
        label="Study group:"
        :label-for="'group'"
        :description="
          published
            ? ''
            : 'Create a new group in the Profile view if none are shown.'
        "
      >
        <b-form-select
          :id="'group'"
          v-model="group.code"
          :options="getGroupOptions"
          required
          :disabled="published || study.code === null"
        ></b-form-select>
      </b-form-group>
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
      <!-- Allows up to a max size and only mp4 files -->
      <b-form-group
        label="Instructions video:"
        :invalid-feedback="invalidFeedbackVideoFile"
        label-for="instructions-video"
        :description="
          'Only .mp4 files allowed. Max size: ' +
          this.max_video_size / (1024 * 1024) +
          'MB'
        "
      >
        <b-form-file
          accept=".mp4"
          id="instructions-video"
          ref="video-input"
          v-model="video_file"
          :state="videoFileState"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
          :disabled="published"
          required
        ></b-form-file>
      </b-form-group>
      <!-- Consent form, only pdf files -->
      <b-form-group
        label="Consent form:"
        label-for="consent-form"
        description="Only pdf files allowed."
      >
        <b-form-file
          accept=".pdf"
          id="consent-form"
          v-model="consent_file"
          :state="consentFileState"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
          :disabled="published"
          required
        ></b-form-file>
      </b-form-group>
      <!-- Textbox of experiment requirements -->
      <b-form-group
        label="Experiment requirements:"
        label-for="requirements"
        description="Add the list of requirements that subjects need to fulfill to participate (e.g. 'Over 18 years old')"
      >
        <b-form-textarea
          id="requirements"
          placeholder="Experiment requirements"
          rows="3"
          max-rows="8"
          v-model="requirements"
          required
        ></b-form-textarea>
      </b-form-group>
      <!-- Textbox of experiment instructions -->
      <b-form-group
        label="Experiment instructions:"
        label-for="instructions"
        description="Instructions that will be shown to the participant just before they start the experiment."
      >
        <b-form-textarea
          id="instructions"
          placeholder="Experiment instructions"
          rows="3"
          max-rows="8"
          v-model="instructions"
          required
        ></b-form-textarea>
      </b-form-group>

      <b-form-group
        description="Turn on if you want the user to know when they input the wrong key in a sequence"
      >
        <b-form-checkbox
          switch
          id="checkbox-feedback"
          v-model="with_feedback"
          name="checkbox-feedback"
          :disabled="published"
        >
          Show Feedback in Trials
        </b-form-checkbox>
      </b-form-group>
      <b-form-group
        description="Turn on if you want the user to know their performance across one block"
      >
        <b-form-checkbox
          switch
          id="checkbox-feedback-blocks"
          v-model="with_feedback_blocks"
          name="checkbox-feedback-blocks"
          :disabled="published"
        >
          Show Block Performance Bar
        </b-form-checkbox>
      </b-form-group>
      <b-form-group
        description="Turn on if you want the user to know their performance across one block"
      >
        <b-form-checkbox
          switch
          id="checkbox-show-instructions"
          v-model="with_shown_instructions"
          name="checkbox-show-instructions"
          :disabled="published"
        >
          Show instructions during experiment
        </b-form-checkbox>
      </b-form-group>
      <!-- Whether to show practice trials or not -->
      <b-form-group
        description="Turn on if you want the user to have some practice trials"
      >
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
      <!-- Practice trials customizer -->
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
          <!-- Whether to have a random sequence or not -->
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
            class="col-4"
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
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col"
            label="Resting time between practice trials and the beginning of experiment(s):"
            :label-for="'rest-pract-exp'"
          >
            <b-form-input
              name="name"
              :id="'rest-pract-exp'"
              v-model.number="rest_after_practice"
              type="number"
              step="0.1"
              required
              placeholder="Resting time between practice and experiment"
              :disabled="published"
            ></b-form-input>
          </b-form-group>
        </div>
      </template>
      <h5>Blocks:</h5>
      <!-- Blocks customizer -->
      <button
        @click="removeAllBlocks"
        class="btn btn-link text-danger"
        :disabled="published"
      >
        Remove all blocks
      </button>
      <div
        class="block-form"
        v-for="(block, index) in experiment_blocks"
        :key="index"
      >
        <p class="font-weight-bold">Block {{ index + 1 }}</p>
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
            <b-form-checkbox
              switch
              v-model="block.is_random_sequence"
              :disabled="published"
            >
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
          <!-- To be shown in the instructions -->
          <b-form-group
            class="col-6"
            label="Hand to use:"
            :label-for="'block-hand-' + index"
          >
            <b-form-select
              :id="'block-hand-' + index"
              v-model="block.hand_to_use"
              :options="hands"
              required
              :disabled="published"
            ></b-form-select>
          </b-form-group>
        </div>
        <div class="form-row">
          <!-- Block type -->
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
          <button
            @click="removeBlock"
            class="btn btn-link text-danger"
            :disabled="published"
          >
            Remove block
          </button>
        </div>
      </div>
      <button @click="addBlock" class="btn btn-link" :disabled="published">
        Add block
      </button>
      <div class="form-row">
        <div class="col">
          <b-button
            type="reset"
            class="btn btn-block"
            variant="danger"
            :disabled="published"
            >Reset</b-button
          >
        </div>
        <div class="col">
          <b-button
            v-if="!submitting"
            type="submit"
            class="btn btn-block"
            variant="primary"
            :disabled="published"
            >Submit</b-button
          >
          <!-- If submitting, show spinner and disable everything, so that it doesn't get clicked multiple times -->
          <b-button
            v-else
            class="btn btn-block"
            variant="primary"
            :disabled="true"
            ><b-spinner label="Spinning"></b-spinner
          ></b-button>
        </div>
      </div>
    </b-form>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      // Experiment properties that are originally inherited from the props (coming from existing experiment if in edit mode, else they are the defaults)
      study: this.prop_study,
      group: this.prop_group,
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
      hands: this.prop_hands,
      video_file: null,
      consent_file: null,
      with_feedback: this.prop_with_feedback,
      with_feedback_blocks: this.prop_with_feedback_blocks,
      with_shown_instructions: this.prop_with_shown_instructions,
      rest_after_practice: this.prop_rest_after_practice,
      requirements: this.prop_requirements,
      instructions: this.prop_instructions,
      submitting: false,
      max_video_size: 32 * 1024 * 1024,
    };
  },
  props: {
    studies: Array,
    experiment_code: String,
    editing: Boolean,
    published: Boolean,
    // Props from default (if creating new) or existing (if editing) experiment
    prop_study: Object,
    prop_group: Object,
    prop_experiment_name: String,
    prop_with_practice_trials: Boolean,
    prop_practice_trials: Number,
    prop_practice_is_random_sequence: Boolean,
    prop_practice_seq_length: Number,
    prop_practice_sequence: String,
    prop_practice_trial_time: Number,
    prop_practice_rest_time: Number,
    prop_rest_after_practice: Number,
    prop_experiment_blocks: Array,
    prop_block_types: Array,
    prop_hands: Array,
    prop_with_feedback: Boolean,
    prop_with_feedback_blocks: Boolean,
    prop_with_shown_instructions: Boolean,
    prop_requirements: String,
    prop_instructions: String,
  },
  computed: {
    getGroupOptions() {
      if (this.study.code !== null) {
        var full_study = this.studies.find(
          (in_study) => in_study.code === this.study.code
        );
        if (!full_study) return [];
        return full_study.groups.map((group) => {
          return { value: group.code, text: `${group.name} (${group.code})` };
        });
      }
      return [];
    },
    videoFileState() {
      if (this.video_file === null) return null;
      if (this.video_file.size > this.max_video_size) return false;
      else return true;
    },
    // Will raise an alert if file size too big.
    invalidFeedbackVideoFile() {
      if (
        this.video_file !== null &&
        this.video_file.size > this.max_video_size
      ) {
        alert(
          "File size too big. Max size is " +
            this.max_video_size / (1024 * 1024) +
            "MB"
        );
        this.video_file = null;
        this.$refs["video-input"].reset();
        return "";
      }
    },
    // Checker to change color status in form input
    consentFileState() {
      if (this.consent_file === null) return null;
      else return true;
    },
  },
  methods: {
    // Adds a new block with all default values to the experiment
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
        hand_to_use: null,
      });
    },
    removeBlock(index) {
      // Removes block from index
      this.experiment_blocks.splice(index, 1);
    },
    removeAllBlocks() {
      // Remove all blocks and add a sample one
      this.experiment_blocks = [];
      this.addBlock();
    },
    onSubmitExperiment(evt) {
      // When submit is clicked
      evt.preventDefault();
      // This two changes are only to disable everything while the request to create the experiment loads
      this.submitting = true;
      this.published = true;

      // Emits an event to the parent javascript file to edit/create the experiment
      this.$emit(
        "submit-experiment",
        this.experiment_name,
        this.study.code,
        this.group.code,
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
        this.with_feedback,
        this.with_feedback_blocks,
        this.with_shown_instructions,
        this.rest_after_practice,
        this.requirements,
        this.instructions
      );
    },
    resetExperiment(evt) {
      // Resets experiment to default values
      evt.preventDefault();

      this.experiment_name = null;
      this.experiment_blocks = [];
      this.addBlock();
    },
  },
};
</script>

<style scoped>
/* Some style to improve appearence of blocks */
.block-form {
  border: 1px solid lightgray;
  padding: 10px;
}
.block-form + .block-form {
  margin-top: 10px;
}
</style>
