<template>
  <div class="container">
    <h1 class="text-center">Experiment {{ exp_code }}</h1>
    <h2>Video instructions</h2>
    <div class="card" style="height: 350px">
      <div class="card-body"></div>
    </div>
    <br />
    <h2>Consent</h2>
    <div class="card" style="height: 350px">
      <div class="card-body"></div>
    </div>
    <br />
    <h2>Sound test</h2>
    <p>
      To make sure the subject is able to clearly listen the tones to be played
    </p>
    <div class="card" style="height: 50px">
      <div class="card-body"></div>
    </div>
    <br />
    <a
      role="button"
      class="btn btn-primary btn-lg btn-block active text-center"
      :href="'/experiment/?code=' + exp_code"
      >Continue to experiment</a
    >
    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {};
  },
  props: {
    exp_code: String,
  },
  mounted: function () {},
  components: {},
  computed: {},
  watch: {},
  methods: {
    isObjectEmpty: function (obj) {
      return Object.keys(obj).length === 0 && obj.constructor === Object;
    },
  },
};
</script>

<style scoped></style>
