<template>
  <div v-if="!isObjectEmpty(current_user)" class="container">
    <h1 class="text-center">Profile</h1>
    <h4>Active experiments:</h4>
    <b-list-group class="col">
      <b-list-group-item
        v-for="experiment in experiments"
        :key="experiment.code"
        class="d-flex justify-content-between align-items-center"
      >
        {{ experiment.name }} ({{ experiment.code }})
        <span>
          <a :href="'/prep_screen/?code=' + experiment.code">Do Experiment</a> |
          <a :href="'/raw_data/?code=' + experiment.code">Download raw data</a>
          |
          <a :href="'/processed_data/?code=' + experiment.code">
            Download processed data</a
          >
          <b-badge
            variant="primary"
            pill
            v-b-tooltip.hover
            :title="experiment.responses + ' responses'"
            >{{ experiment.responses }}</b-badge
          >
        </span>
      </b-list-group-item>
    </b-list-group>
    <br />
    <a href="/profile/create_experiment" class="btn btn-primary"
      >Create Experiment</a
    >
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {};
  },
  props: {
    current_user: Object,
    experiments: Array,
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