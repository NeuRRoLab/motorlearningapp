<template>
    <div class="container">
        <h1 class="text-center">Create new Experiment</h2>
        <b-form @submit="onSubmitExperiment" @reset="resetExperiment">
            <b-form-group
                label="Experiment Name:"
                label-for="name"
            >
                <b-form-input
                    name="name"
                    id="name"
                    v-model="experiment_name"
                    type="text"
                    required
                    placeholder="Name"
                ></b-form-input>
            </b-form-group>
            <h5>Blocks:</h5>
            <div class="block-form"
                v-for="(block, index) in experiment_blocks"
                :key="index">
                <div class="form-row">
                    <b-form-group
                        class="col"
                        label="Sequence:"
                        :label-for="'sequence-'+index"
                    >
                        <b-form-input
                            name="name"
                            :id="'sequence-'+index"
                            v-model="block.sequence"
                            type="text"
                            required
                            placeholder="Sequence of characters"
                        ></b-form-input>
                    </b-form-group>
                    <b-form-group
                        class="col"
                        label="Maximum time (s) per trial:"
                        :label-for="'max-time-'+index"
                    >
                        <b-form-input
                            name="name"
                            :id="'max-time-'+index"
                            v-model="block.max_time_per_trial"
                            type="number"
                            required
                            placeholder="Maximum time per trial"
                        ></b-form-input>
                    </b-form-group>
                    <b-form-group
                        class="col"
                        label="Resting time (s):"
                        :label-for="'resting-'+index"
                    >
                        <b-form-input
                            name="name"
                            :id="'resting-'+index"
                            v-model="block.resting_time"
                            type="number"
                            required
                            placeholder="Resting time between trials"
                        ></b-form-input>
                    </b-form-group>
                </div>
                <div class="form-row">
                    <b-form-group class="col-6" label="Block type:" :label-for="'block-type'+index">
                        <b-form-select
                            :id="'block-type'+index"
                            v-model="block.block_type"
                            :options="block_types"
                            required
                        ></b-form-select>
                    </b-form-group>
                    <b-form-group v-if="block.block_type === 'num_trials'" class="col" label="Number of Trials:" :label-for="'num-trials'+index">
                        <b-form-input
                            :id="'num-trials-'+index"
                            v-model="block.num_trials"
                            type="number"
                            required
                            placeholder="Total number of trials"
                        ></b-form-input>
                    </b-form-group>
                    <b-form-group v-if="block.block_type === 'max_time'" class="col" label="Maximum time (s):" :label-for="'max-time'+index">
                        <b-form-input
                            :id="'max-time-'+index"
                            v-model="block.max_time"
                            type="number"
                            required
                            placeholder="Maximum time (seconds)"
                        ></b-form-input>
                    </b-form-group>
                </div>
                <button @click="removeBlock" class="btn btn-link text-danger">Remove block</button>
            </div>
            <button @click="addBlock" class="btn btn-link">Add block</button>
            <div class="form-row">
                <div class="col">
                    <b-button type="reset" class="btn btn-block" variant="danger">Reset</b-button>
                </div>
                <div class="col">
                    <b-button type="submit" class="btn btn-block" variant="primary">Submit</b-button>
                </div>
            </div>
        </b-form>
    </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
        experiment_name: null,
        experiment_blocks: [{
            sequence: null,
            max_time_per_trial: null,
            resting_time: null,
            block_type: null,
            num_trials: null,
            max_time: null,
        }],
        block_types: [
            { value: null, text: 'Please select a block type' },
            { value: 'max_time', text: 'Maximum time' },
            { value: 'num_trials', text: 'Number of trials' },
        ],
    };
  },
  props: {
  },
  mounted: function () {
  },
  components: {
      'nav-bar': httpVueLoader('/static/gestureApp/js/components/NavBar.vue'),
  },
  computed: {},
  watch: {},
  methods: {
      addBlock() {
          this.experiment_blocks.push({
            sequence: null,
            max_time_per_trial: null,
            resting_time: null,
            block_type: null,
            num_trials: null,
            max_time: null,
          })
      },
      removeBlock(index) {
          this.experiment_blocks.splice(index, 1);
      },
      onSubmitExperiment(evt) {
          evt.preventDefault();

          this.$emit('submit-experiment', this.experiment_name, this.experiment_blocks)
      },
      resetExperiment(evt) {
          evt.preventDefault();
          
          this.experiment_name = null,
          this.experiment_blocks = [{
            sequence: null,
            max_time_per_trial: null,
            resting_time: null,
            block_type: null,
            num_trials: null,
            max_time: null,
        }]
      }
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
