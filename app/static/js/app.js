'use strict';

angular.module('foodAdvisor', [
   //Self created dependencies
  'foodAdvisor.controllers',
  'foodAdvisor.services',
  'foodAdvisor.directives',

   //3rd party dependencies
  'ngResource',
  'ngRoute',
  'ui.bootstrap',
  'ui.date',
  'angucomplete',
  'upload.button'
]).
config(function ($routeProvider, $locationProvider) {
  $routeProvider.
    when('/', {
      templateUrl: 'views/home.html',
      controller: ''
    }).
    when('/how', {
      templateUrl: 'views/how.html',
      controller: ''
    }).
    when('/about', {
      templateUrl: 'views/about.html',
      controller: ''
    }).
    otherwise({
      redirectTo: '/'
    });
  $locationProvider.html5Mode(true);
});
