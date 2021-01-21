<template>
  <div class="container">
    <!-- Will have to do a practice example -->
    <notifications
      group="alerts"
      position="top right"
      :max="2"
      :duration="6000"
    ></notifications>
    <h2>
      Experiment {{ code
      }}<span class="text-success">{{ practicing ? ": Practicing" : "" }}</span>
    </h2>
    <div v-if="!experiment_started && !practicing" class="row">
      <div class="col text-center">
        <button
          v-if="remaining_practice_trials > 0"
          class="btn btn-primary"
          @click="startPractice"
        >
          Practice
        </button>
        <button v-else class="btn btn-primary" @click="startExperiment">
          Start Experiment
        </button>
      </div>
    </div>
    <template v-else-if="practicing">
      <div class="col-md-12 text-center">
        <button class="btn btn-primary text-center" @click="stopPractice">
          Stop Practice
        </button>
      </div>
      <p class="text-center">Enter the keys in order when they appear.</p>
      <trial
        ref="practice-trial"
        :practice="true"
        :max_time_per_trial="5"
        :resting_time="5"
        @trial-ended="practiceTrialEnded"
      ></trial>
    </template>
    <template v-else-if="experiment_started && !experiment_finished">
      <h4>Experiment Progress</h4>
      <b-progress height="2rem" :max="blocks.length" show-progress>
        <b-progress-bar
          :value="current_block + 1"
          :label="
            'Block ' +
            (current_block + 1).toString() +
            ' of ' +
            blocks.length.toString()
          "
        ></b-progress-bar>
      </b-progress>
      <br />
      <!-- Show block type -->
      <p class="text-center">
        Block type:
        {{
          isTypeNumTrials
            ? "Maximum number of trials -> " + blocks[current_block].num_trials
            : "Maximum time -> " + blocks[current_block].max_time + " seconds"
        }}
      </p>
      <div v-if="!block_started" class="text-center">
        <button class="btn btn-primary" @click="startBlock">Start Block</button>
      </div>

      <template v-else>
        <h4>Block Progress</h4>
        <b-progress
          v-if="isTypeNumTrials"
          height="2rem"
          :max="blocks[current_block].num_trials"
          show-progress
        >
          <b-progress-bar
            :value="current_trial + 1"
            :label="
              'Trial ' +
              (current_trial + 1).toString() +
              ' of ' +
              blocks[current_block].num_trials.toString()
            "
          ></b-progress-bar>
        </b-progress>
        <div v-else>
          <countdown
            ref="timerBlock"
            :time="blocks[current_block].max_time * 1000"
            :interval="1000"
            :auto-start="true"
            @progress="blockTimerProgress"
            @end="blockEnded(true)"
          >
          </countdown>
          <b-progress
            height="2rem"
            :max="blocks[current_block].max_time"
            show-progress
          >
            <b-progress-bar
              :value="current_block_time"
              :label="
                current_block_time.toString() +
                ' seconds of ' +
                blocks[current_block].max_time.toString()
              "
            ></b-progress-bar>
          </b-progress>
        </div>
        <br />

        <trial
          v-bind="getTrialObj"
          @trial-ended="trialEnded"
          @rest-ended="restEnded"
        >
        </trial>

        <h4>Block performance</h4>
        <b-progress
          height="2rem"
          :max="num_correct_seq + num_incorrect_seq"
          show-progress
        >
          <b-progress-bar
            :value="num_correct_seq"
            :label="num_correct_seq.toString() + ' correct'"
            variant="success"
          ></b-progress-bar>
          <b-progress-bar
            :value="num_incorrect_seq"
            :label="num_incorrect_seq.toString() + ' incorrect'"
            variant="danger"
          ></b-progress-bar>
        </b-progress>
      </template>
    </template>
    <div v-else class="text-center">
      <button
        class="btn btn-primary"
        @click="$emit('send-data', experiment_blocks)"
      >
        Send Data
      </button>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      practicing: false,
      practice_finished: false,
      remaining_practice_trials: 0,

      experiment_started: false,
      experiment_finished: false,
      block_started: false,
      current_block: 0,
      current_block_time: 0,
      current_trial: 0,
      num_correct_seq: 0,
      num_incorrect_seq: 0,
      resting: false,
      capturing_keypresses: false,
      current_inputted_sequence: [],

      started_trial_at: null,
      keypresses_trial: [],
      block_trials: [],
      experiment_blocks: [],
    };
  },
  props: {
    code: String,
    blocks: Array,
    practice_trials: Number,
  },
  mounted: function () {
    console.log(this.blocks);
    // window.addEventListener('keydown', this.keydownHandler);
    this.remaining_practice_trials = this.practice_trials;
  },
  components: {
    trial: httpVueLoader("/static/gestureApp/js/components/Trial.vue"),
  },
  computed: {
    getTrialObj() {
      return {
        sequence: this.blocks[this.current_block].sequence,
        resting: this.resting,
        max_time_per_trial: this.blocks[this.current_block].max_time_per_trial,
        resting_time: this.blocks[this.current_block].resting_time,
      };
    },
    isTypeNumTrials() {
      if (this.blocks[this.current_block].type === "num_trials") return true;
      return false;
    },
  },
  watch: {},
  methods: {
    startExperiment: function () {
      this.experiment_started = true;
      //   this.startTrial();
    },
    startPractice() {
      this.practicing = true;
    },
    stopPractice() {
      console.log(this.$refs["practice-trial"]);
      this.$refs["practice-trial"].stopPractice();
      this.practicing = false;
    },
    startBlock: function () {
      this.block_started = true;
      this.capturing_keypresses = true;
      this.current_block_time = 0;
      this.startTrial();
    },
    startTrial: function () {
      //   setTimeout(() => this.$refs.timerTrial.start(), 5);
      this.started_trial_at = new Date().getTime();
      console.log("starting trial");
    },
    practiceTrialEnded(correct, keypresses_trial, inputted_sequence, sequence) {
      if (correct) {
        console.log("Correct sequence!!");
        this.$notify({
          group: "alerts",
          title: "Correct input sequence",
          type: "success",
        });
      } else {
        console.log("incorrect sequence");
        this.$notify({
          group: "alerts",
          title: "Error in input sequence",
          text: `
                Target sequence was '${sequence}', and your input was '${inputted_sequence.join(
            ""
          )}'
                `,
          type: `error`,
        });
      }
      this.remaining_practice_trials--;
      if (this.remaining_practice_trials <= 0) this.stopPractice();
    },
    trialEnded: function (
      correct,
      keypresses_trial,
      inputted_sequence,
      sequence
    ) {
      console.log("Trial ended");

      if (correct) {
        console.log("Correct sequence!!");
        this.$notify({
          group: "alerts",
          title: "Correct input sequence",
          type: "success",
        });
        this.num_correct_seq++;
      } else {
        console.log("incorrect sequence");
        this.$notify({
          group: "alerts",
          title: "Error in input sequence",
          text: `
                Target sequence was '${sequence}', and your input was '${inputted_sequence.join(
            ""
          )}'
                `,
          type: `error`,
        });
        this.num_incorrect_seq++;
      }
      this.block_trials.push({
        started_at: this.started_trial_at,
        keypresses: keypresses_trial,
        correct: correct,
      });
      this.started_trial_at = null;
    },
    restEnded: function () {
      console.log("restEnded");
      //   Go to the next trial if there is one
      if (
        !this.isTypeNumTrials ||
        (this.isTypeNumTrials &&
          this.current_trial + 1 < this.blocks[this.current_block].num_trials)
      ) {
        console.log("rest ended");
        this.current_trial++;
        this.startTrial();
      }
      // Check if there are any blocks left
      else if (this.current_block + 1 < this.blocks.length) {
        this.blockEnded();
      } else this.blockEnded(true);
    },
    blockEnded: function (from_timer = false) {
      this.experiment_blocks.push(this.block_trials);
      this.block_trials = new Array();
      this.current_trial = 0;
      this.num_correct_seq = 0;
      this.num_incorrect_seq = 0;
      this.block_started = false;
      this.capturing_keypresses = false;

      if (from_timer) {
        if (this.current_block + 1 >= this.blocks.length)
          this.experimentEnded();
      } else this.current_block++;
    },
    experimentEnded: function () {
      console.log("experiment ended");
      // this.experiment_blocks.push(this.block_trials)
      this.block_trials = new Array();
      this.current_block = 0;
      this.current_trial = 0;
      this.num_correct_seq = 0;
      this.num_incorrect_seq = 0;
      this.block_started = false;
      this.capturing_keypresses = false;

      this.experiment_finished = true;
    },
    blockTimerProgress(data) {
      this.current_block_time =
        this.blocks[this.current_block].max_time -
        (data.hours * 3600 + data.minutes * 60 + data.seconds);
    },
  },
};
</script>

<style scoped>
.seq-charact {
  border: 1px solid black;
  display: inline-block;
  width: 100px;
  padding: 40px 0;
  background-color: lightgray;
  text-align: center;
  font-size: 40px;
}
h2 {
  text-align: center;
}
.top-buffer {
  margin-top: 10px;
}
</style>
