<template>
  <div>
    <nav-bar> </nav-bar>
    <div class="container">
      <!-- Will have to do a practice example -->
      <notifications group="alerts" position="top right" :max="2" :duration="6000"></notifications>
      <h2>Experiment {{ code }}</h2>
      <div v-if="!experiment_started" class="row">
        <div class="col text-center">
          <button class="btn btn-primary" @click="startExperiment">
            Start Experiment
          </button>
        </div>
      </div>
      <template v-else-if="!experiment_finished">
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
        <br>
        <!-- Show block type -->
        <p class="text-center">Block type: {{ isTypeNumTrials ? 'Maximum number of trials -> ' + blocks[current_block].num_trials : 'Maximum time -> ' + blocks[current_block].max_time + ' seconds'}}</p>
        <div v-if="!block_started" class="text-center">
          <button class="btn btn-primary" @click="startBlock">Start Block</button>
        </div>
        
        <template v-else>
          <h4>Block Progress</h4>
          <b-progress v-if="isTypeNumTrials" height="2rem" :max="blocks[current_block].num_trials" show-progress>
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
            <b-progress height="2rem" :max="blocks[current_block].max_time" show-progress>
              <b-progress-bar
                :value="current_block_time"
                :label="
                  (current_block_time).toString() +
                  ' seconds of ' +
                  blocks[current_block].max_time.toString()
                "
              ></b-progress-bar>
            </b-progress>
          </div>
          <br>
          
          <template v-if="!resting">
            <h4 class="text-center">Enter Key Sequence:</h4>
            <div class="text-center">
              <div :ref="'seq-'+(index-1)" :value="blocks[current_block].sequence[index-1]" v-for="index in blocks[current_block].sequence.length" class="seq-charact" :key="index-1">
                {{ blocks[current_block].sequence[index-1] }}
              </div>
            </div>
            <p class="text-center">
              Time left:
              <countdown
                ref="timerTrial"
                :time="blocks[current_block].max_time_per_trial * 1000"
                :interval="1000"
                :auto-start="true"
                @end="trialEnded"
              >
                <template slot-scope="props"
                  >{{ props.seconds }} seconds.</template
                >
              </countdown>
            </p>
          </template>
          <template v-else>
            <h1 class="text-center">Rest</h1>
            <p class="text-center">
              Time left:
              <countdown
                ref="timerRest"
                :time="blocks[current_block].resting_time * 1000"
                :interval="1000"
                :auto-start="false"
                :emit-events="true"
                @progress="restProgress"
                @end="restEnded"
              >
                <span slot-scope="props"
                  >{{ props.seconds }} seconds.</span
                >
              </countdown>
            </p>
          </template>

          <h4>Block performance</h4>
          <b-progress height="2rem" :max="num_correct_seq + num_incorrect_seq" show-progress>
            <b-progress-bar
              :value="num_correct_seq"
              :label="num_correct_seq.toString() + ' correct'"
              variant="success"
            ></b-progress-bar>
            <b-progress-bar
              :value="num_incorrect_seq"
              :label="(num_incorrect_seq).toString() + ' incorrect'"
              variant="danger"
            ></b-progress-bar>
          </b-progress>
        </template>
      </template>
      <div v-else class="text-center">
          <button class="btn btn-primary" @click="$emit('send-data',experiment_blocks)">Send Data</button>
      </div>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
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
  },
  mounted: function () {
    console.log(this.blocks);
    window.addEventListener('keydown', this.keydownHandler);
  },
  components: {
    'nav-bar': httpVueLoader('/static/gestureApp/js/components/NavBar.vue'),
  },
  computed: {
    isTypeNumTrials() {
      if (this.blocks[this.current_block].type === 'num_trials')
        return true;
      return false;
    }
  },
  watch: {},
  methods: {
    startExperiment: function () {
      this.experiment_started = true;
    //   this.startTrial();
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
      console.log('starting trial')
    },
    trialEnded: function () {
      console.log("Trial ended");
      this.resting = true;
      this.capturing_keypresses = false;
      this.was_correct = false;
    
      if (this.current_inputted_sequence.join("") === this.blocks[this.current_block].sequence) {
        console.log('Correct sequence!!');
        this.$notify({
          group: 'alerts',
          title: 'Correct input sequence',
          type: 'success',
        });
        this.num_correct_seq++;
        this.was_correct = true;
      }
      else {
        console.log('incorrect sequence')
          this.$notify({
            group: 'alerts',
            title: 'Error in input sequence',
            text: `
                Target sequence was '${this.blocks[this.current_block].sequence}', and your input was '${this.current_inputted_sequence.join("")}'
                `,
            type: `error`,
            });
          this.num_incorrect_seq++;
          this.was_correct = false;
      }
      this.block_trials.push({started_at: this.started_trial_at, keypresses: this.keypresses_trial, correct: this.was_correct});
      this.started_trial_at = null;
      this.keypresses_trial = new Array(); 
      
      this.$nextTick(() => {
        this.$refs.timerRest.start();
      })
      this.current_inputted_sequence = []
    },
    restEnded: function () {
        console.log("restEnded");
        this.resting = false;
        //   Go to the next trial if there is one
        if (!this.isTypeNumTrials || (this.isTypeNumTrials && this.current_trial + 1 < this.blocks[this.current_block].num_trials))
        {
          console.log('rest ended')
            this.capturing_keypresses = true;
            this.current_trial++;
            this.startTrial();
        }
        // Check if there are any blocks left
        else if (this.current_block + 1 < this.blocks.length) {
            this.blockEnded();
        } 
        else this.blockEnded(true);
    },
    restProgress() {
      console.log('rest progress')
    },
    blockEnded: function (from_timer=false) {
        this.experiment_blocks.push(this.block_trials)
        this.block_trials = new Array();
        this.current_trial = 0;
        this.num_correct_seq = 0;
        this.num_incorrect_seq = 0;
        this.block_started = false;
        this.capturing_keypresses = false;

        if (from_timer) {
          if (this.current_block + 1 >= this.blocks.length)
            this.experimentEnded();
        }
        else
          this.current_block++;

        
    },
    experimentEnded: function () {
        console.log('experiment ended');
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
    keydownHandler: function (e) {
        if (this.capturing_keypresses) {
          // TODO: Only count digits as keypresses
            var timestamp = new Date().getTime();
            this.current_inputted_sequence.push(e.key)
            this.keypresses_trial.push({value: e.key, timestamp: timestamp});
            // Check if the inputted key is correct
            var index = this.current_inputted_sequence.length - 1;
            if (this.current_inputted_sequence.length > this.blocks[this.current_block].sequence.length) {
                this.incorrectInputSequence();
            }
            else if (this.blocks[this.current_block].sequence[index] === e.key) {
                console.log('they are equal!!');
                this.$refs['seq-'+index.toString()][0].style.backgroundColor = 'green';
            }
            else {
                this.$refs['seq-'+index.toString()][0].style.backgroundColor = 'red';
                this.incorrectInputSequence();
            }
            // Correct sequence!
            if (this.current_inputted_sequence.join("") === this.blocks[this.current_block].sequence)
              this.$refs.timerTrial.end();
        }
    },
    incorrectInputSequence: function () {
        // this.capturing_keypresses = false;
        console.log('incorrectInputSequence')
        this.$refs.timerTrial.end();
    },
    blockTimerProgress(data) {
      this.current_block_time = this.blocks[this.current_block].max_time - (data.hours * 3600 + data.minutes * 60 + data.seconds);
    }
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
