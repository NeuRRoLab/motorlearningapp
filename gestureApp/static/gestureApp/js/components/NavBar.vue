<template>
    <div>
        <b-navbar toggleable="sm" type="light" variant="success">
        <b-navbar-toggle target="nav-text-collapse"></b-navbar-toggle>
        <b-navbar-brand href="/">Experiment App</b-navbar-brand>

        <b-navbar-nav class="ml-auto">
            <b-nav-item href="/profile">Profile</b-nav-item>
            <b-nav-item href="/login">Login</b-nav-item>
            <b-nav-item href="/logout">Logout</b-nav-item>
        </b-navbar-nav>
        </b-navbar>
    </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
    };
  },
  props: {
  },
  mounted: function () {
  },
  components: {},
  computed: {},
  watch: {},
  methods: {
  },
};
</script>

<style scoped>
</style>
