!function(t) {
    "function" == typeof define && define.amd ? define(["jquery"], t) : "object" == typeof exports ? t(require("jquery")) : t(jQuery)
}(function(x, V) {
    function S() {
        return new Date(Date.UTC.apply(Date, arguments))
    }
    function F() {
        var t = new Date;
        return S(t.getFullYear(), t.getMonth(), t.getDate())
    }
    function n(t, e) {
        return t.getUTCFullYear() === e.getUTCFullYear() && t.getUTCMonth() === e.getUTCMonth() && t.getUTCDate() === e.getUTCDate()
    }
    function t(t, e) {
        return function() {
            return e !== V && x.fn.datepicker.deprecated(e),
            this[t].apply(this, arguments)
        }
    }
    function k(t, e) {
        x.data(t, "datepicker", this),
        this._events = [],
        this._secondaryEvents = [],
        this._process_options(e),
        this.dates = new i,
        this.viewDate = this.o.defaultViewDate,
        this.focusDate = null,
        this.element = x(t),
        this.isInput = this.element.is("input"),
        this.inputField = this.isInput ? this.element : this.element.find("input"),
        this.component = !!this.element.hasClass("date") && this.element.find(".add-on, .input-group-addon, .input-group-append, .input-group-prepend, .btn"),
        this.component && 0 === this.component.length && (this.component = !1),
        this.isInline = !this.component && this.element.is("div"),
        this.picker = x(N.template),
        this._check_template(this.o.templates.leftArrow) && this.picker.find(".prev").html(this.o.templates.leftArrow),
        this._check_template(this.o.templates.rightArrow) && this.picker.find(".next").html(this.o.templates.rightArrow),
        this._buildEvents(),
        this._attachEvents(),
        this.isInline ? this.picker.addClass("datepicker-inline").appendTo(this.element) : this.picker.addClass("datepicker-dropdown dropdown-menu"),
        this.o.rtl && this.picker.addClass("datepicker-rtl"),
        this.o.calendarWeeks && this.picker.find(".datepicker-days .datepicker-switch, thead .datepicker-title, tfoot .today, tfoot .clear").attr("colspan", function(t, e) {
            return Number(e) + 1
        }),
        this._process_options({
            startDate: this._o.startDate,
            endDate: this._o.endDate,
            daysOfWeekDisabled: this.o.daysOfWeekDisabled,
            daysOfWeekHighlighted: this.o.daysOfWeekHighlighted,
            datesDisabled: this.o.datesDisabled
        }),
        this._allow_update = !1,
        this.setViewMode(this.o.startView),
        this._allow_update = !0,
        this.fillDow(),
        this.fillMonths(),
        this.update(),
        this.isInline && this.show()
    }
    var e, i = (e = {
        get: function(t) {
            return this.slice(t)[0]
        },
        contains: function(t) {
            for (var e = t && t.valueOf(), i = 0, a = this.length; i < a; i++)
                if (0 <= this[i].valueOf() - e && this[i].valueOf() - e < 864e5)
                    return i;
            return -1
        },
        remove: function(t) {
            this.splice(t, 1)
        },
        replace: function(t) {
            t && (x.isArray(t) || (t = [t]),
            this.clear(),
            this.push.apply(this, t))
        },
        clear: function() {
            this.length = 0
        },
        copy: function() {
            var t = new i;
            return t.replace(this),
            t
        }
    },
    function() {
        var t = [];
        return t.push.apply(t, arguments),
        x.extend(t, e),
        t
    }
    );
    k.prototype = {
        constructor: k,
        _resolveViewName: function(i) {
            return x.each(N.viewModes, function(t, e) {
                if (i === t || -1 !== x.inArray(i, e.names))
                    return i = t,
                    !1
            }),
            i
        },
        _resolveDaysOfWeek: function(t) {
            return x.isArray(t) || (t = t.split(/[,\s]*/)),
            x.map(t, Number)
        },
        _check_template: function(t) {
            try {
                return t === V || "" === t ? !1 : (t.match(/[<>]/g) || []).length <= 0 || 0 < x(t).length
            } catch (t) {
                return !1
            }
        },
        _process_options: function(t) {
            this._o = x.extend({}, this._o, t);
            var e = this.o = x.extend({}, this._o)
              , i = e.language;
            A[i] || (i = i.split("-")[0],
            A[i] || (i = d.language)),
            e.language = i,
            e.startView = this._resolveViewName(e.startView),
            e.minViewMode = this._resolveViewName(e.minViewMode),
            e.maxViewMode = this._resolveViewName(e.maxViewMode),
            e.startView = Math.max(this.o.minViewMode, Math.min(this.o.maxViewMode, e.startView)),
            !0 !== e.multidate && (e.multidate = Number(e.multidate) || !1,
            !1 !== e.multidate && (e.multidate = Math.max(0, e.multidate))),
            e.multidateSeparator = String(e.multidateSeparator),
            e.weekStart %= 7,
            e.weekEnd = (e.weekStart + 6) % 7;
            var a = N.parseFormat(e.format);
            e.startDate !== -1 / 0 && (e.startDate ? e.startDate instanceof Date ? e.startDate = this._local_to_utc(this._zero_time(e.startDate)) : e.startDate = N.parseDate(e.startDate, a, e.language, e.assumeNearbyYear) : e.startDate = -1 / 0),
            e.endDate !== 1 / 0 && (e.endDate ? e.endDate instanceof Date ? e.endDate = this._local_to_utc(this._zero_time(e.endDate)) : e.endDate = N.parseDate(e.endDate, a, e.language, e.assumeNearbyYear) : e.endDate = 1 / 0),
            e.daysOfWeekDisabled = this._resolveDaysOfWeek(e.daysOfWeekDisabled || []),
            e.daysOfWeekHighlighted = this._resolveDaysOfWeek(e.daysOfWeekHighlighted || []),
            e.datesDisabled = e.datesDisabled || [],
            x.isArray(e.datesDisabled) || (e.datesDisabled = e.datesDisabled.split(",")),
            e.datesDisabled = x.map(e.datesDisabled, function(t) {
                return N.parseDate(t, a, e.language, e.assumeNearbyYear)
            });
            var s, n, o, r = String(e.orientation).toLowerCase().split(/\s+/g), h = e.orientation.toLowerCase(), r = x.grep(r, function(t) {
                return /^auto|left|right|top|bottom$/.test(t)
            });
            if (e.orientation = {
                x: "auto",
                y: "auto"
            },
            h && "auto" !== h)
                if (1 === r.length)
                    switch (r[0]) {
                    case "top":
                    case "bottom":
                        e.orientation.y = r[0];
                        break;
                    case "left":
                    case "right":
                        e.orientation.x = r[0]
                    }
                else
                    h = x.grep(r, function(t) {
                        return /^left|right$/.test(t)
                    }),
                    e.orientation.x = h[0] || "auto",
                    h = x.grep(r, function(t) {
                        return /^top|bottom$/.test(t)
                    }),
                    e.orientation.y = h[0] || "auto";
            else
                ;e.defaultViewDate instanceof Date || "string" == typeof e.defaultViewDate ? e.defaultViewDate = N.parseDate(e.defaultViewDate, a, e.language, e.assumeNearbyYear) : e.defaultViewDate ? (s = e.defaultViewDate.year || (new Date).getFullYear(),
            n = e.defaultViewDate.month || 0,
            o = e.defaultViewDate.day || 1,
            e.defaultViewDate = S(s, n, o)) : e.defaultViewDate = F()
        },
        _applyEvents: function(t) {
            for (var e, i, a, s = 0; s < t.length; s++)
                e = t[s][0],
                2 === t[s].length ? (i = V,
                a = t[s][1]) : 3 === t[s].length && (i = t[s][1],
                a = t[s][2]),
                e.on(a, i)
        },
        _unapplyEvents: function(t) {
            for (var e, i, a, s = 0; s < t.length; s++)
                e = t[s][0],
                2 === t[s].length ? (a = V,
                i = t[s][1]) : 3 === t[s].length && (a = t[s][1],
                i = t[s][2]),
                e.off(i, a)
        },
        _buildEvents: function() {
            var t = {
                keyup: x.proxy(function(t) {
                    -1 === x.inArray(t.keyCode, [27, 37, 39, 38, 40, 32, 13, 9]) && this.update()
                }, this),
                keydown: x.proxy(this.keydown, this),
                paste: x.proxy(this.paste, this)
            };
            !0 === this.o.showOnFocus && (t.focus = x.proxy(this.show, this)),
            this.isInput ? this._events = [[this.element, t]] : this.component && this.inputField.length ? this._events = [[this.inputField, t], [this.component, {
                click: x.proxy(this.show, this)
            }]] : this._events = [[this.element, {
                click: x.proxy(this.show, this),
                keydown: x.proxy(this.keydown, this)
            }]],
            this._events.push([this.element, "*", {
                blur: x.proxy(function(t) {
                    this._focused_from = t.target
                }, this)
            }], [this.element, {
                blur: x.proxy(function(t) {
                    this._focused_from = t.target
                }, this)
            }]),
            this.o.immediateUpdates && this._events.push([this.element, {
                "changeYear changeMonth": x.proxy(function(t) {
                    this.update(t.date)
                }, this)
            }]),
            this._secondaryEvents = [[this.picker, {
                click: x.proxy(this.click, this)
            }], [this.picker, ".prev, .next", {
                click: x.proxy(this.navArrowsClick, this)
            }], [this.picker, ".day:not(.disabled)", {
                click: x.proxy(this.dayCellClick, this)
            }], [x(window), {
                resize: x.proxy(this.place, this)
            }], [x(document), {
                "mousedown touchstart": x.proxy(function(t) {
                    this.element.is(t.target) || this.element.find(t.target).length || this.picker.is(t.target) || this.picker.find(t.target).length || this.isInline || this.hide()
                }, this)
            }]]
        },
        _attachEvents: function() {
            this._detachEvents(),
            this._applyEvents(this._events)
        },
        _detachEvents: function() {
            this._unapplyEvents(this._events)
        },
        _attachSecondaryEvents: function() {
            this._detachSecondaryEvents(),
            this._applyEvents(this._secondaryEvents)
        },
        _detachSecondaryEvents: function() {
            this._unapplyEvents(this._secondaryEvents)
        },
        _trigger: function(t, e) {
            var i = e || this.dates.get(-1)
              , a = this._utc_to_local(i);
            this.element.trigger({
                type: t,
                date: a,
                viewMode: this.viewMode,
                dates: x.map(this.dates, this._utc_to_local),
                format: x.proxy(function(t, e) {
                    0 === arguments.length ? (t = this.dates.length - 1,
                    e = this.o.format) : "string" == typeof t && (e = t,
                    t = this.dates.length - 1),
                    e = e || this.o.format;
                    var i = this.dates.get(t);
                    return N.formatDate(i, e, this.o.language)
                }, this)
            })
        },
        show: function() {
            if (!(this.inputField.is(":disabled") || this.inputField.prop("readonly") && !1 === this.o.enableOnReadonly))
                return this.isInline || this.picker.appendTo(this.o.container),
                this.place(),
                this.picker.show(),
                this._attachSecondaryEvents(),
                this._trigger("show"),
                (window.navigator.msMaxTouchPoints || "ontouchstart"in document) && this.o.disableTouchKeyboard && x(this.element).blur(),
                this
        },
        hide: function() {
            return this.isInline || !this.picker.is(":visible") || (this.focusDate = null,
            this.picker.hide().detach(),
            this._detachSecondaryEvents(),
            this.setViewMode(this.o.startView),
            this.o.forceParse && this.inputField.val() && this.setValue(),
            this._trigger("hide")),
            this
        },
        destroy: function() {
            return this.hide(),
            this._detachEvents(),
            this._detachSecondaryEvents(),
            this.picker.remove(),
            delete this.element.data().datepicker,
            this.isInput || delete this.element.data().date,
            this
        },
        paste: function(t) {
            var e;
            if (t.originalEvent.clipboardData && t.originalEvent.clipboardData.types && -1 !== x.inArray("text/plain", t.originalEvent.clipboardData.types))
                e = t.originalEvent.clipboardData.getData("text/plain");
            else {
                if (!window.clipboardData)
                    return;
                e = window.clipboardData.getData("Text")
            }
            this.setDate(e),
            this.update(),
            t.preventDefault()
        },
        _utc_to_local: function(t) {
            if (!t)
                return t;
            var e = new Date(t.getTime() + 6e4 * t.getTimezoneOffset());
            return e.getTimezoneOffset() !== t.getTimezoneOffset() && (e = new Date(t.getTime() + 6e4 * e.getTimezoneOffset())),
            e
        },
        _local_to_utc: function(t) {
            return t && new Date(t.getTime() - 6e4 * t.getTimezoneOffset())
        },
        _zero_time: function(t) {
            return t && new Date(t.getFullYear(),t.getMonth(),t.getDate())
        },
        _zero_utc_time: function(t) {
            return t && S(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate())
        },
        getDates: function() {
            return x.map(this.dates, this._utc_to_local)
        },
        getUTCDates: function() {
            return x.map(this.dates, function(t) {
                return new Date(t)
            })
        },
        getDate: function() {
            return this._utc_to_local(this.getUTCDate())
        },
        getUTCDate: function() {
            var t = this.dates.get(-1);
            return t !== V ? new Date(t) : null
        },
        clearDates: function() {
            this.inputField.val(""),
            this.update(),
            this._trigger("changeDate"),
            this.o.autoclose && this.hide()
        },
        setDates: function() {
            var t = x.isArray(arguments[0]) ? arguments[0] : arguments;
            return this.update.apply(this, t),
            this._trigger("changeDate"),
            this.setValue(),
            this
        },
        setUTCDates: function() {
            var t = x.isArray(arguments[0]) ? arguments[0] : arguments;
            return this.setDates.apply(this, x.map(t, this._utc_to_local)),
            this
        },
        setDate: t("setDates"),
        setUTCDate: t("setUTCDates"),
        remove: t("destroy", "Method `remove` is deprecated and will be removed in version 2.0. Use `destroy` instead"),
        setValue: function() {
            var t = this.getFormattedDate();
            return this.inputField.val(t),
            this
        },
        getFormattedDate: function(e) {
            e === V && (e = this.o.format);
            var i = this.o.language;
            return x.map(this.dates, function(t) {
                return N.formatDate(t, e, i)
            }).join(this.o.multidateSeparator)
        },
        getStartDate: function() {
            return this.o.startDate
        },
        setStartDate: function(t) {
            return this._process_options({
                startDate: t
            }),
            this.update(),
            this.updateNavArrows(),
            this
        },
        getEndDate: function() {
            return this.o.endDate
        },
        setEndDate: function(t) {
            return this._process_options({
                endDate: t
            }),
            this.update(),
            this.updateNavArrows(),
            this
        },
        setDaysOfWeekDisabled: function(t) {
            return this._process_options({
                daysOfWeekDisabled: t
            }),
            this.update(),
            this
        },
        setDaysOfWeekHighlighted: function(t) {
            return this._process_options({
                daysOfWeekHighlighted: t
            }),
            this.update(),
            this
        },
        setDatesDisabled: function(t) {
            return this._process_options({
                datesDisabled: t
            }),
            this.update(),
            this
        },
        place: function() {
            if (this.isInline)
                return this;
            var t = this.picker.outerWidth()
              , e = this.picker.outerHeight()
              , i = x(this.o.container)
              , a = i.width()
              , s = "body" === this.o.container ? x(document).scrollTop() : i.scrollTop()
              , n = i.offset()
              , o = [0];
            this.element.parents().each(function() {
                var t = x(this).css("z-index");
                "auto" !== t && 0 !== Number(t) && o.push(Number(t))
            });
            var r = Math.max.apply(Math, o) + this.o.zIndexOffset
              , h = this.component ? this.component.parent().offset() : this.element.offset()
              , l = this.component ? this.component.outerHeight(!0) : this.element.outerHeight(!1)
              , d = this.component ? this.component.outerWidth(!0) : this.element.outerWidth(!1)
              , c = h.left - n.left
              , u = h.top - n.top;
            "body" !== this.o.container && (u += s),
            this.picker.removeClass("datepicker-orient-top datepicker-orient-bottom datepicker-orient-right datepicker-orient-left"),
            "auto" !== this.o.orientation.x ? (this.picker.addClass("datepicker-orient-" + this.o.orientation.x),
            "right" === this.o.orientation.x && (c -= t - d)) : h.left < 0 ? (this.picker.addClass("datepicker-orient-left"),
            c -= h.left - 10) : a < c + t ? (this.picker.addClass("datepicker-orient-right"),
            c += d - t) : this.o.rtl ? this.picker.addClass("datepicker-orient-right") : this.picker.addClass("datepicker-orient-left");
            var p, f = this.o.orientation.y;
            return "auto" === f && (f = -s + u - e < 0 ? "bottom" : "top"),
            this.picker.addClass("datepicker-orient-" + f),
            "top" === f ? u -= e + parseInt(this.picker.css("padding-top")) : u += l,
            this.o.rtl ? (p = a - (c + d),
            this.picker.css({
                top: u,
                right: p,
                zIndex: r
            })) : this.picker.css({
                top: u,
                left: c,
                zIndex: r
            }),
            this
        },
        _allow_update: !0,
        update: function() {
            if (!this._allow_update)
                return this;
            var t = this.dates.copy()
              , i = []
              , e = !1;
            return arguments.length ? (x.each(arguments, x.proxy(function(t, e) {
                e instanceof Date && (e = this._local_to_utc(e)),
                i.push(e)
            }, this)),
            e = !0) : (i = (i = this.isInput ? this.element.val() : this.element.data("date") || this.inputField.val()) && this.o.multidate ? i.split(this.o.multidateSeparator) : [i],
            delete this.element.data().date),
            i = x.map(i, x.proxy(function(t) {
                return N.parseDate(t, this.o.format, this.o.language, this.o.assumeNearbyYear)
            }, this)),
            i = x.grep(i, x.proxy(function(t) {
                return !this.dateWithinRange(t) || !t
            }, this), !0),
            this.dates.replace(i),
            this.o.updateViewDate && (this.dates.length ? this.viewDate = new Date(this.dates.get(-1)) : this.viewDate < this.o.startDate ? this.viewDate = new Date(this.o.startDate) : this.viewDate > this.o.endDate ? this.viewDate = new Date(this.o.endDate) : this.viewDate = this.o.defaultViewDate),
            e ? (this.setValue(),
            this.element.change()) : this.dates.length && String(t) !== String(this.dates) && e && (this._trigger("changeDate"),
            this.element.change()),
            !this.dates.length && t.length && (this._trigger("clearDate"),
            this.element.change()),
            this.fill(),
            this
        },
        fillDow: function() {
            if (this.o.showWeekDays) {
                var t = this.o.weekStart
                  , e = "<tr>";
                for (this.o.calendarWeeks && (e += '<th class="cw">&#160;</th>'); t < this.o.weekStart + 7; )
                    e += '<th class="dow',
                    -1 !== x.inArray(t, this.o.daysOfWeekDisabled) && (e += " disabled"),
                    e += '">' + A[this.o.language].daysMin[t++ % 7] + "</th>";
                e += "</tr>",
                this.picker.find(".datepicker-days thead").append(e)
            }
        },
        fillMonths: function() {
            for (var t = this._utc_to_local(this.viewDate), e = "", i = 0; i < 12; i++)
                e += '<span class="month' + (t && t.getMonth() === i ? " focused" : "") + '">' + A[this.o.language].monthsShort[i] + "</span>";
            this.picker.find(".datepicker-months td").html(e)
        },
        setRange: function(t) {
            t && t.length ? this.range = x.map(t, function(t) {
                return t.valueOf()
            }) : delete this.range,
            this.fill()
        },
        getClassNames: function(t) {
            var e = []
              , i = this.viewDate.getUTCFullYear()
              , a = this.viewDate.getUTCMonth()
              , s = F();
            return t.getUTCFullYear() < i || t.getUTCFullYear() === i && t.getUTCMonth() < a ? e.push("old") : (t.getUTCFullYear() > i || t.getUTCFullYear() === i && t.getUTCMonth() > a) && e.push("new"),
            this.focusDate && t.valueOf() === this.focusDate.valueOf() && e.push("focused"),
            this.o.todayHighlight && n(t, s) && e.push("today"),
            -1 !== this.dates.contains(t) && e.push("active"),
            this.dateWithinRange(t) || e.push("disabled"),
            this.dateIsDisabled(t) && e.push("disabled", "disabled-date"),
            -1 !== x.inArray(t.getUTCDay(), this.o.daysOfWeekHighlighted) && e.push("highlighted"),
            this.range && (t > this.range[0] && t < this.range[this.range.length - 1] && e.push("range"),
            -1 !== x.inArray(t.valueOf(), this.range) && e.push("selected"),
            t.valueOf() === this.range[0] && e.push("range-start"),
            t.valueOf() === this.range[this.range.length - 1] && e.push("range-end")),
            e
        },
        _fill_yearsView: function(t, e, i, a, s, n, o) {
            for (var r, h, l, d = "", c = i / 10, u = this.picker.find(t), p = Math.floor(a / i) * i, f = p + 9 * c, g = Math.floor(this.viewDate.getFullYear() / c) * c, D = x.map(this.dates, function(t) {
                return Math.floor(t.getUTCFullYear() / c) * c
            }), m = p - c; m <= f + c; m += c)
                r = [e],
                h = null,
                m === p - c ? r.push("old") : m === f + c && r.push("new"),
                -1 !== x.inArray(m, D) && r.push("active"),
                (m < s || n < m) && r.push("disabled"),
                m === g && r.push("focused"),
                o !== x.noop && ((l = o(new Date(m,0,1))) === V ? l = {} : "boolean" == typeof l ? l = {
                    enabled: l
                } : "string" == typeof l && (l = {
                    classes: l
                }),
                !1 === l.enabled && r.push("disabled"),
                l.classes && (r = r.concat(l.classes.split(/\s+/))),
                l.tooltip && (h = l.tooltip)),
                d += '<span class="' + r.join(" ") + '"' + (h ? ' title="' + h + '"' : "") + ">" + m + "</span>";
            u.find(".datepicker-switch").text(p + "-" + f),
            u.find("td").html(d)
        },
        fill: function() {
            var t, e, i = new Date(this.viewDate), s = i.getUTCFullYear(), a = i.getUTCMonth(), n = this.o.startDate !== -1 / 0 ? this.o.startDate.getUTCFullYear() : -1 / 0, o = this.o.startDate !== -1 / 0 ? this.o.startDate.getUTCMonth() : -1 / 0, r = this.o.endDate !== 1 / 0 ? this.o.endDate.getUTCFullYear() : 1 / 0, h = this.o.endDate !== 1 / 0 ? this.o.endDate.getUTCMonth() : 1 / 0, l = A[this.o.language].today || A.en.today || "", d = A[this.o.language].clear || A.en.clear || "", c = A[this.o.language].titleFormat || A.en.titleFormat, u = F(), p = (!0 === this.o.todayBtn || "linked" === this.o.todayBtn) && u >= this.o.startDate && u <= this.o.endDate && !this.weekOfDateIsDisabled(u);
            if (!isNaN(s) && !isNaN(a)) {
                this.picker.find(".datepicker-days .datepicker-switch").text(N.formatDate(i, c, this.o.language)),
                this.picker.find("tfoot .today").text(l).css("display", p ? "table-cell" : "none"),
                this.picker.find("tfoot .clear").text(d).css("display", !0 === this.o.clearBtn ? "table-cell" : "none"),
                this.picker.find("thead .datepicker-title").text(this.o.title).css("display", "string" == typeof this.o.title && "" !== this.o.title ? "table-cell" : "none"),
                this.updateNavArrows(),
                this.fillMonths();
                var f = S(s, a, 0)
                  , g = f.getUTCDate();
                f.setUTCDate(g - (f.getUTCDay() - this.o.weekStart + 7) % 7);
                var D = new Date(f);
                f.getUTCFullYear() < 100 && D.setUTCFullYear(f.getUTCFullYear()),
                D.setUTCDate(D.getUTCDate() + 42),
                D = D.valueOf();
                for (var m, y, v, w, k, b, _ = []; f.valueOf() < D; ) {
                    (b = f.getUTCDay()) === this.o.weekStart && (_.push("<tr>"),
                    this.o.calendarWeeks && (y = new Date(+f + (this.o.weekStart - b - 7) % 7 * 864e5),
                    v = new Date(Number(y) + (11 - y.getUTCDay()) % 7 * 864e5),
                    w = new Date(Number(w = S(v.getUTCFullYear(), 0, 1)) + (11 - w.getUTCDay()) % 7 * 864e5),
                    k = (v - w) / 864e5 / 7 + 1,
                    _.push('<td class="cw">' + k + "</td>"))),
                    (m = this.getClassNames(f)).push("day");
                    var C = f.getUTCDate();
                    this.o.beforeShowDay !== x.noop && ((e = this.o.beforeShowDay(this._utc_to_local(f))) === V ? e = {} : "boolean" == typeof e ? e = {
                        enabled: e
                    } : "string" == typeof e && (e = {
                        classes: e
                    }),
                    !1 === e.enabled && m.push("disabled"),
                    e.classes && (m = m.concat(e.classes.split(/\s+/))),
                    e.tooltip && (t = e.tooltip),
                    e.content && (C = e.content)),
                    m = x.isFunction(x.uniqueSort) ? x.uniqueSort(m) : x.unique(m),
                    _.push('<td class="' + m.join(" ") + '"' + (t ? ' title="' + t + '"' : "") + ' data-date="' + f.getTime().toString() + '">' + C + "</td>"),
                    t = null,
                    b === this.o.weekEnd && _.push("</tr>"),
                    f.setUTCDate(f.getUTCDate() + 1)
                }
                this.picker.find(".datepicker-days tbody").html(_.join(""));
                var T, M = A[this.o.language].monthsTitle || A.en.monthsTitle || "Months", U = this.picker.find(".datepicker-months").find(".datepicker-switch").text(this.o.maxViewMode < 2 ? M : s).end().find("tbody span").removeClass("active");
                x.each(this.dates, function(t, e) {
                    e.getUTCFullYear() === s && U.eq(e.getUTCMonth()).addClass("active")
                }),
                (s < n || r < s) && U.addClass("disabled"),
                s === n && U.slice(0, o).addClass("disabled"),
                s === r && U.slice(h + 1).addClass("disabled"),
                this.o.beforeShowMonth !== x.noop && (T = this,
                x.each(U, function(t, e) {
                    var i = new Date(s,t,1)
                      , a = T.o.beforeShowMonth(i);
                    a === V ? a = {} : "boolean" == typeof a ? a = {
                        enabled: a
                    } : "string" == typeof a && (a = {
                        classes: a
                    }),
                    !1 !== a.enabled || x(e).hasClass("disabled") || x(e).addClass("disabled"),
                    a.classes && x(e).addClass(a.classes),
                    a.tooltip && x(e).prop("title", a.tooltip)
                })),
                this._fill_yearsView(".datepicker-years", "year", 10, s, n, r, this.o.beforeShowYear),
                this._fill_yearsView(".datepicker-decades", "decade", 100, s, n, r, this.o.beforeShowDecade),
                this._fill_yearsView(".datepicker-centuries", "century", 1e3, s, n, r, this.o.beforeShowCentury)
            }
        },
        updateNavArrows: function() {
            if (this._allow_update) {
                var t, e, i = new Date(this.viewDate), a = i.getUTCFullYear(), s = i.getUTCMonth(), n = this.o.startDate !== -1 / 0 ? this.o.startDate.getUTCFullYear() : -1 / 0, o = this.o.startDate !== -1 / 0 ? this.o.startDate.getUTCMonth() : -1 / 0, r = this.o.endDate !== 1 / 0 ? this.o.endDate.getUTCFullYear() : 1 / 0, h = this.o.endDate !== 1 / 0 ? this.o.endDate.getUTCMonth() : 1 / 0, l = 1;
                switch (this.viewMode) {
                case 4:
                    l *= 10;
                case 3:
                    l *= 10;
                case 2:
                    l *= 10;
                case 1:
                    t = Math.floor(a / l) * l <= n,
                    e = Math.floor(a / l) * l + l > r;
                    break;
                case 0:
                    t = a <= n && s <= o,
                    e = r <= a && h <= s
                }
                this.picker.find(".prev").toggleClass("disabled", t),
                this.picker.find(".next").toggleClass("disabled", e)
            }
        },
        click: function(t) {
            var e, i, a;
            t.preventDefault(),
            t.stopPropagation(),
            (e = x(t.target)).hasClass("datepicker-switch") && this.viewMode !== this.o.maxViewMode && this.setViewMode(this.viewMode + 1),
            e.hasClass("today") && !e.hasClass("day") && (this.setViewMode(0),
            this._setDate(F(), "linked" === this.o.todayBtn ? null : "view")),
            e.hasClass("clear") && this.clearDates(),
            e.hasClass("disabled") || (e.hasClass("month") || e.hasClass("year") || e.hasClass("decade") || e.hasClass("century")) && (this.viewDate.setUTCDate(1),
            1 === this.viewMode ? (a = e.parent().find("span").index(e),
            i = this.viewDate.getUTCFullYear(),
            this.viewDate.setUTCMonth(a)) : (a = 0,
            i = Number(e.text()),
            this.viewDate.setUTCFullYear(i)),
            this._trigger(N.viewModes[this.viewMode - 1].e, this.viewDate),
            this.viewMode === this.o.minViewMode ? this._setDate(S(i, a, 1)) : (this.setViewMode(this.viewMode - 1),
            this.fill())),
            this.picker.is(":visible") && this._focused_from && this._focused_from.focus(),
            delete this._focused_from
        },
        dayCellClick: function(t) {
            var e = x(t.currentTarget).data("date")
              , i = new Date(e);
            this.o.updateViewDate && (i.getUTCFullYear() !== this.viewDate.getUTCFullYear() && this._trigger("changeYear", this.viewDate),
            i.getUTCMonth() !== this.viewDate.getUTCMonth() && this._trigger("changeMonth", this.viewDate)),
            this._setDate(i)
        },
        navArrowsClick: function(t) {
            var e = x(t.currentTarget).hasClass("prev") ? -1 : 1;
            0 !== this.viewMode && (e *= 12 * N.viewModes[this.viewMode].navStep),
            this.viewDate = this.moveMonth(this.viewDate, e),
            this._trigger(N.viewModes[this.viewMode].e, this.viewDate),
            this.fill()
        },
        _toggle_multidate: function(t) {
            var e = this.dates.contains(t);
            if (t || this.dates.clear(),
            -1 !== e ? (!0 === this.o.multidate || 1 < this.o.multidate || this.o.toggleActive) && this.dates.remove(e) : (!1 === this.o.multidate && this.dates.clear(),
            this.dates.push(t)),
            "number" == typeof this.o.multidate)
                for (; this.dates.length > this.o.multidate; )
                    this.dates.remove(0)
        },
        _setDate: function(t, e) {
            e && "date" !== e || this._toggle_multidate(t && new Date(t)),
            (!e && this.o.updateViewDate || "view" === e) && (this.viewDate = t && new Date(t)),
            this.fill(),
            this.setValue(),
            e && "view" === e || this._trigger("changeDate"),
            this.inputField.trigger("change"),
            !this.o.autoclose || e && "date" !== e || this.hide()
        },
        moveDay: function(t, e) {
            var i = new Date(t);
            return i.setUTCDate(t.getUTCDate() + e),
            i
        },
        moveWeek: function(t, e) {
            return this.moveDay(t, 7 * e)
        },
        moveMonth: function(t, e) {
            if (!(i = t) || isNaN(i.getTime()))
                return this.o.defaultViewDate;
            var i;
            if (!e)
                return t;
            var a, s, n = new Date(t.valueOf()), o = n.getUTCDate(), r = n.getUTCMonth(), h = Math.abs(e);
            if (e = 0 < e ? 1 : -1,
            1 === h)
                s = -1 === e ? function() {
                    return n.getUTCMonth() === r
                }
                : function() {
                    return n.getUTCMonth() !== a
                }
                ,
                a = r + e,
                n.setUTCMonth(a),
                a = (a + 12) % 12;
            else {
                for (var l = 0; l < h; l++)
                    n = this.moveMonth(n, e);
                a = n.getUTCMonth(),
                n.setUTCDate(o),
                s = function() {
                    return a !== n.getUTCMonth()
                }
            }
            for (; s(); )
                n.setUTCDate(--o),
                n.setUTCMonth(a);
            return n
        },
        moveYear: function(t, e) {
            return this.moveMonth(t, 12 * e)
        },
        moveAvailableDate: function(t, e, i) {
            do {
                if (t = this[i](t, e),
                !this.dateWithinRange(t))
                    return !1;
                i = "moveDay"
            } while (this.dateIsDisabled(t));
            return t
        },
        weekOfDateIsDisabled: function(t) {
            return -1 !== x.inArray(t.getUTCDay(), this.o.daysOfWeekDisabled)
        },
        dateIsDisabled: function(e) {
            return this.weekOfDateIsDisabled(e) || 0 < x.grep(this.o.datesDisabled, function(t) {
                return n(e, t)
            }).length
        },
        dateWithinRange: function(t) {
            return t >= this.o.startDate && t <= this.o.endDate
        },
        keydown: function(t) {
            if (this.picker.is(":visible")) {
                var e, i, a = !1, s = this.focusDate || this.viewDate;
                switch (t.keyCode) {
                case 27:
                    this.focusDate ? (this.focusDate = null,
                    this.viewDate = this.dates.get(-1) || this.viewDate,
                    this.fill()) : this.hide(),
                    t.preventDefault(),
                    t.stopPropagation();
                    break;
                case 37:
                case 38:
                case 39:
                case 40:
                    if (!this.o.keyboardNavigation || 7 === this.o.daysOfWeekDisabled.length)
                        break;
                    e = 37 === t.keyCode || 38 === t.keyCode ? -1 : 1,
                    0 === this.viewMode ? t.ctrlKey ? (i = this.moveAvailableDate(s, e, "moveYear")) && this._trigger("changeYear", this.viewDate) : t.shiftKey ? (i = this.moveAvailableDate(s, e, "moveMonth")) && this._trigger("changeMonth", this.viewDate) : 37 === t.keyCode || 39 === t.keyCode ? i = this.moveAvailableDate(s, e, "moveDay") : this.weekOfDateIsDisabled(s) || (i = this.moveAvailableDate(s, e, "moveWeek")) : 1 === this.viewMode ? (38 !== t.keyCode && 40 !== t.keyCode || (e *= 4),
                    i = this.moveAvailableDate(s, e, "moveMonth")) : 2 === this.viewMode && (38 !== t.keyCode && 40 !== t.keyCode || (e *= 4),
                    i = this.moveAvailableDate(s, e, "moveYear")),
                    i && (this.focusDate = this.viewDate = i,
                    this.setValue(),
                    this.fill(),
                    t.preventDefault());
                    break;
                case 13:
                    if (!this.o.forceParse)
                        break;
                    s = this.focusDate || this.dates.get(-1) || this.viewDate,
                    this.o.keyboardNavigation && (this._toggle_multidate(s),
                    a = !0),
                    this.focusDate = null,
                    this.viewDate = this.dates.get(-1) || this.viewDate,
                    this.setValue(),
                    this.fill(),
                    this.picker.is(":visible") && (t.preventDefault(),
                    t.stopPropagation(),
                    this.o.autoclose && this.hide());
                    break;
                case 9:
                    this.focusDate = null,
                    this.viewDate = this.dates.get(-1) || this.viewDate,
                    this.fill(),
                    this.hide()
                }
                a && (this.dates.length ? this._trigger("changeDate") : this._trigger("clearDate"),
                this.inputField.trigger("change"))
            } else
                40 !== t.keyCode && 27 !== t.keyCode || (this.show(),
                t.stopPropagation())
        },
        setViewMode: function(t) {
            this.viewMode = t,
            this.picker.children("div").hide().filter(".datepicker-" + N.viewModes[this.viewMode].clsName).show(),
            this.updateNavArrows(),
            this._trigger("changeViewMode", new Date(this.viewDate))
        }
    };
    function l(t, e) {
        x.data(t, "datepicker", this),
        this.element = x(t),
        this.inputs = x.map(e.inputs, function(t) {
            return t.jquery ? t[0] : t
        }),
        delete e.inputs,
        this.keepEmptyValues = e.keepEmptyValues,
        delete e.keepEmptyValues,
        s.call(x(this.inputs), e).on("changeDate", x.proxy(this.dateUpdated, this)),
        this.pickers = x.map(this.inputs, function(t) {
            return x.data(t, "datepicker")
        }),
        this.updateDates()
    }
    l.prototype = {
        updateDates: function() {
            this.dates = x.map(this.pickers, function(t) {
                return t.getUTCDate()
            }),
            this.updateRanges()
        },
        updateRanges: function() {
            var i = x.map(this.dates, function(t) {
                return t.valueOf()
            });
            x.each(this.pickers, function(t, e) {
                e.setRange(i)
            })
        },
        clearDates: function() {
            x.each(this.pickers, function(t, e) {
                e.clearDates()
            })
        },
        dateUpdated: function(t) {
            if (!this.updating) {
                this.updating = !0;
                var i = x.data(t.target, "datepicker");
                if (i !== V) {
                    var a = i.getUTCDate()
                      , s = this.keepEmptyValues
                      , e = x.inArray(t.target, this.inputs)
                      , n = e - 1
                      , o = e + 1
                      , r = this.inputs.length;
                    if (-1 !== e) {
                        if (x.each(this.pickers, function(t, e) {
                            e.getUTCDate() || e !== i && s || e.setUTCDate(a)
                        }),
                        a < this.dates[n])
                            for (; 0 <= n && a < this.dates[n]; )
                                this.pickers[n--].setUTCDate(a);
                        else if (a > this.dates[o])
                            for (; o < r && a > this.dates[o]; )
                                this.pickers[o++].setUTCDate(a);
                        this.updateDates(),
                        delete this.updating
                    }
                }
            }
        },
        destroy: function() {
            x.map(this.pickers, function(t) {
                t.destroy()
            }),
            x(this.inputs).off("changeDate", this.dateUpdated),
            delete this.element.data().datepicker
        },
        remove: t("destroy", "Method `remove` is deprecated and will be removed in version 2.0. Use `destroy` instead")
    };
    var a = x.fn.datepicker
      , s = function(o) {
        var r, h = Array.apply(null, arguments);
        if (h.shift(),
        this.each(function() {
            var t, e, i, a = x(this), s = a.data("datepicker"), n = "object" == typeof o && o;
            s || (t = function(t, e) {
                var i = x(t).data()
                  , a = {}
                  , s = new RegExp("^" + e.toLowerCase() + "([A-Z])");
                function n(t, e) {
                    return e.toLowerCase()
                }
                for (var o in e = new RegExp("^" + e.toLowerCase()),
                i)
                    e.test(o) && (a[o.replace(s, n)] = i[o]);
                return a
            }(this, "date"),
            e = function(t) {
                var i = {};
                if (A[t] || (t = t.split("-")[0],
                A[t])) {
                    var a = A[t];
                    return x.each(c, function(t, e) {
                        e in a && (i[e] = a[e])
                    }),
                    i
                }
            }(x.extend({}, d, t, n).language),
            i = x.extend({}, d, e, t, n),
            s = a.hasClass("input-daterange") || i.inputs ? (x.extend(i, {
                inputs: i.inputs || a.find("input").toArray()
            }),
            new l(this,i)) : new k(this,i),
            a.data("datepicker", s)),
            "string" == typeof o && "function" == typeof s[o] && (r = s[o].apply(s, h))
        }),
        r === V || r instanceof k || r instanceof l)
            return this;
        if (1 < this.length)
            throw new Error("Using only allowed for the collection of a single element (" + o + " function)");
        return r
    };
    x.fn.datepicker = s;
    var d = x.fn.datepicker.defaults = {
        assumeNearbyYear: !1,
        autoclose: !1,
        beforeShowDay: x.noop,
        beforeShowMonth: x.noop,
        beforeShowYear: x.noop,
        beforeShowDecade: x.noop,
        beforeShowCentury: x.noop,
        calendarWeeks: !1,
        clearBtn: !1,
        toggleActive: !1,
        daysOfWeekDisabled: [],
        daysOfWeekHighlighted: [],
        datesDisabled: [],
        endDate: 1 / 0,
        forceParse: !0,
        format: "mm/dd/yyyy",
        keepEmptyValues: !1,
        keyboardNavigation: !0,
        language: "en",
        minViewMode: 0,
        maxViewMode: 4,
        multidate: !1,
        multidateSeparator: ",",
        orientation: "auto",
        rtl: !1,
        startDate: -1 / 0,
        startView: 0,
        todayBtn: !1,
        todayHighlight: !1,
        updateViewDate: !0,
        weekStart: 0,
        disableTouchKeyboard: !1,
        enableOnReadonly: !0,
        showOnFocus: !0,
        zIndexOffset: 10,
        container: "body",
        immediateUpdates: !1,
        title: "",
        templates: {
            leftArrow: "&#x00AB;",
            rightArrow: "&#x00BB;"
        },
        showWeekDays: !0
    }
      , c = x.fn.datepicker.locale_opts = ["format", "rtl", "weekStart"];
    x.fn.datepicker.Constructor = k;
    var A = x.fn.datepicker.dates = {
        en: {
            days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            daysMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            today: "Today",
            clear: "Clear",
            titleFormat: "MM yyyy"
        }
    }
      , N = {
        viewModes: [{
            names: ["days", "month"],
            clsName: "days",
            e: "changeMonth"
        }, {
            names: ["months", "year"],
            clsName: "months",
            e: "changeYear",
            navStep: 1
        }, {
            names: ["years", "decade"],
            clsName: "years",
            e: "changeDecade",
            navStep: 10
        }, {
            names: ["decades", "century"],
            clsName: "decades",
            e: "changeCentury",
            navStep: 100
        }, {
            names: ["centuries", "millennium"],
            clsName: "centuries",
            e: "changeMillennium",
            navStep: 1e3
        }],
        validParts: /dd?|DD?|mm?|MM?|yy(?:yy)?/g,
        nonpunctuation: /[^ -\/:-@\u5e74\u6708\u65e5\[-`{-~\t\n\r]+/g,
        parseFormat: function(t) {
            if ("function" == typeof t.toValue && "function" == typeof t.toDisplay)
                return t;
            var e = t.replace(this.validParts, "\0").split("\0")
              , i = t.match(this.validParts);
            if (!e || !e.length || !i || 0 === i.length)
                throw new Error("Invalid date format.");
            return {
                separators: e,
                parts: i
            }
        },
        parseDate: function(t, e, i, s) {
            if (!t)
                return V;
            if (t instanceof Date)
                return t;
            if ("string" == typeof e && (e = N.parseFormat(e)),
            e.toValue)
                return e.toValue(t, e, i);
            var a, n, o, r, h = {
                d: "moveDay",
                m: "moveMonth",
                w: "moveWeek",
                y: "moveYear"
            }, l = {
                yesterday: "-1d",
                today: "+0d",
                tomorrow: "+1d"
            };
            if (t in l && (t = l[t]),
            /^[\-+]\d+[dmwy]([\s,]+[\-+]\d+[dmwy])*$/i.test(t)) {
                for (a = t.match(/([\-+]\d+)([dmwy])/gi),
                t = new Date,
                v = 0; v < a.length; v++)
                    n = a[v].match(/([\-+]\d+)([dmwy])/i),
                    o = Number(n[1]),
                    r = h[n[2].toLowerCase()],
                    t = k.prototype[r](t, o);
                return k.prototype._zero_utc_time(t)
            }
            a = t && t.match(this.nonpunctuation) || [];
            var d, c, u = {}, p = ["yyyy", "yy", "M", "MM", "m", "mm", "d", "dd"], f = {
                yyyy: function(t, e) {
                    return t.setUTCFullYear(s ? (!0 === (a = s) && (a = 10),
                    (i = e) < 100 && (i += 2e3) > (new Date).getFullYear() + a && (i -= 100),
                    i) : e);
                    var i, a
                },
                m: function(t, e) {
                    if (isNaN(t))
                        return t;
                    for (--e; e < 0; )
                        e += 12;
                    for (e %= 12,
                    t.setUTCMonth(e); t.getUTCMonth() !== e; )
                        t.setUTCDate(t.getUTCDate() - 1);
                    return t
                },
                d: function(t, e) {
                    return t.setUTCDate(e)
                }
            };
            f.yy = f.yyyy,
            f.M = f.MM = f.mm = f.m,
            f.dd = f.d,
            t = F();
            var g = e.parts.slice();
            function D() {
                var t = this.slice(0, a[v].length)
                  , e = a[v].slice(0, t.length);
                return t.toLowerCase() === e.toLowerCase()
            }
            if (a.length !== g.length && (g = x(g).filter(function(t, e) {
                return -1 !== x.inArray(e, p)
            }).toArray()),
            a.length === g.length) {
                for (var m, y, v = 0, w = g.length; v < w; v++) {
                    if (d = parseInt(a[v], 10),
                    n = g[v],
                    isNaN(d))
                        switch (n) {
                        case "MM":
                            c = x(A[i].months).filter(D),
                            d = x.inArray(c[0], A[i].months) + 1;
                            break;
                        case "M":
                            c = x(A[i].monthsShort).filter(D),
                            d = x.inArray(c[0], A[i].monthsShort) + 1
                        }
                    u[n] = d
                }
                for (v = 0; v < p.length; v++)
                    (y = p[v])in u && !isNaN(u[y]) && (m = new Date(t),
                    f[y](m, u[y]),
                    isNaN(m) || (t = m))
            }
            return t
        },
        formatDate: function(t, e, i) {
            if (!t)
                return "";
            if ("string" == typeof e && (e = N.parseFormat(e)),
            e.toDisplay)
                return e.toDisplay(t, e, i);
            var a = {
                d: t.getUTCDate(),
                D: A[i].daysShort[t.getUTCDay()],
                DD: A[i].days[t.getUTCDay()],
                m: t.getUTCMonth() + 1,
                M: A[i].monthsShort[t.getUTCMonth()],
                MM: A[i].months[t.getUTCMonth()],
                yy: t.getUTCFullYear().toString().substring(2),
                yyyy: t.getUTCFullYear()
            };
            a.dd = (a.d < 10 ? "0" : "") + a.d,
            a.mm = (a.m < 10 ? "0" : "") + a.m,
            t = [];
            for (var s = x.extend([], e.separators), n = 0, o = e.parts.length; n <= o; n++)
                s.length && t.push(s.shift()),
                t.push(a[e.parts[n]]);
            return t.join("")
        },
        headTemplate: '<thead><tr><th colspan="7" class="datepicker-title"></th></tr><tr><th class="prev">' + d.templates.leftArrow + '</th><th colspan="5" class="datepicker-switch"></th><th class="next">' + d.templates.rightArrow + "</th></tr></thead>",
        contTemplate: '<tbody><tr><td colspan="7"></td></tr></tbody>',
        footTemplate: '<tfoot><tr><th colspan="7" class="today"></th></tr><tr><th colspan="7" class="clear"></th></tr></tfoot>'
    };
    N.template = '<div class="datepicker"><div class="datepicker-days"><table class="table-condensed">' + N.headTemplate + "<tbody></tbody>" + N.footTemplate + '</table></div><div class="datepicker-months"><table class="table-condensed">' + N.headTemplate + N.contTemplate + N.footTemplate + '</table></div><div class="datepicker-years"><table class="table-condensed">' + N.headTemplate + N.contTemplate + N.footTemplate + '</table></div><div class="datepicker-decades"><table class="table-condensed">' + N.headTemplate + N.contTemplate + N.footTemplate + '</table></div><div class="datepicker-centuries"><table class="table-condensed">' + N.headTemplate + N.contTemplate + N.footTemplate + "</table></div></div>",
    x.fn.datepicker.DPGlobal = N,
    x.fn.datepicker.noConflict = function() {
        return x.fn.datepicker = a,
        this
    }
    ,
    x.fn.datepicker.version = "1.9.0",
    x.fn.datepicker.deprecated = function(t) {
        var e = window.console;
        e && e.warn && e.warn("DEPRECATED: " + t)
    }
    ,
    x(document).on("focus.datepicker.data-api click.datepicker.data-api", '[data-provide="datepicker"]', function(t) {
        var e = x(this);
        e.data("datepicker") || (t.preventDefault(),
        s.call(e, "show"))
    }),
    x(function() {
        s.call(x('[data-provide="datepicker-inline"]'))
    })
});
