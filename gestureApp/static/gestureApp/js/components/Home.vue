<template>
  <div class="container justify-content-center">
    <div class="experiment-form">
      <b-form @submit="goToExperiment">
        <div class="form-row">
          <b-form-group
            class="col"
            id="input-group"
            label="Experiment Code:"
            label-for="input"
          >
            <b-form-input
              name="code"
              id="input"
              v-model="experiment_code"
              type="text"
              :maxlength="4"
              required
              placeholder="Code"
              @input="onInput"
            ></b-form-input>
          </b-form-group>
        </div>
        <b-form-group
          label="Have you done an experiment here before?"
          v-slot="{ ariaDescribedby }"
        >
          <b-form-radio-group
            id="radio-group-2"
            v-model="answer"
            :aria-describedby="ariaDescribedby"
            name="radio-sub-component"
            required
          >
            <b-form-radio :value="true">Yes</b-form-radio>
            <b-form-radio :value="false">No</b-form-radio>
          </b-form-radio-group>
        </b-form-group>
        <template v-if="answer !== null">
          <template v-if="!answer">
            <button @click="generateCode" class="btn btn-link text-primary row">
              Generate subject code
            </button>
            <b-card v-if="subject_code">
              <b-card-text>
                <span class="font-weight-bold">Your Subject Code:</span>
                {{ this.subject_code }}
              </b-card-text>
              <b-card-text>Save this code for future experiments.</b-card-text>
              <b-form inline>
                <label class="sr-only" for="inline-form-input-name"
                  >Email</label
                >
                <b-form-input
                  id="inline-form-input-name"
                  class="mb-2 mr-sm-2 mb-sm-0"
                  placeholder="name@example.com"
                  v-model="email"
                ></b-form-input>
                <input type="text" style="display: none" />
                <b-button
                  variant="primary"
                  @click="
                    $emit('send-subject-code', email);
                    email = '';
                  "
                  >Send code to email</b-button
                >
              </b-form>
              <b-card-text v-if="email_response !== ''">{{
                email_response
              }}</b-card-text>
            </b-card>
            <br />
          </template>
          <div v-if="answer || subject_code.length > 0" class="form-row">
            <b-form-group
              class="col"
              id="input-group"
              label="Subject Code:"
              label-for="subj-code"
            >
              <b-form-input
                name="subj-code"
                id="subj-code"
                v-model="subject_code_input"
                type="text"
                :maxlength="subject_code_seq_length"
                placeholder="Subject Code"
                required
              ></b-form-input>
            </b-form-group>
          </div>
        </template>

        <b-button
          type="submit"
          class="btn btn-block"
          variant="primary"
          :disabled="subject_code_input.length !== subject_code_seq_length"
          >Submit</b-button
        >
      </b-form>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      experiment_code: "",
      subject_code_input: "",
      email: "",
      answer: null,
      subject_code_seq_length: 16,
    };
  },
  props: {
    subject_code: String,
    email_response: String,
  },
  mounted: function () {},
  components: {
    "nav-bar": httpVueLoader("/static/gestureApp/js/components/NavBar.vue"),
  },
  computed: {},
  watch: {
    subject_code: function (newVal, oldVal) {
      this.subject_code_input = newVal;
    },
  },
  methods: {
    onInput: function (input) {
      this.experiment_code = input.toUpperCase();
    },
    goToExperiment(evt) {
      evt.preventDefault();
      window.location.href = `/experiment/${this.experiment_code}/?subj-code=${this.subject_code_input}`;
    },
    generateCode(evt) {
      evt.preventDefault();
      this.$emit("generate-code");
    },
  },
};
</script>

<style scoped>
.experiment-form {
  border: 1px solid lightgray;
  width: 730px;
  padding: 40px;
  float: none;
  margin: 0 auto;
  border-radius: 5px;
}
</style>
